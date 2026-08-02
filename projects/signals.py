from django.db import transaction
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import Project


MEDIA_FIELDS = ("thumbnail", "report")


def _schedule_file_deletion(field_name, name, storage, using):
    if not name:
        return

    def delete_if_unreferenced():
        if not (
            Project.objects.using(using)
            .filter(**{field_name: name})
            .exists()
        ):
            storage.delete(name)

    transaction.on_commit(delete_if_unreferenced, using=using)


@receiver(pre_save, sender=Project)
def remember_previous_project_media(sender, instance, using, **kwargs):
    if not instance.pk:
        return

    try:
        previous = (
            sender.objects.using(using)
            .only(*MEDIA_FIELDS)
            .get(pk=instance.pk)
        )
    except sender.DoesNotExist:
        return

    instance._previous_media_names = {
        field_name: getattr(previous, field_name).name
        for field_name in MEDIA_FIELDS
        if getattr(previous, field_name)
    }


@receiver(post_save, sender=Project)
def delete_replaced_project_media(sender, instance, using, **kwargs):
    previous_names = getattr(instance, "_previous_media_names", {})

    for field_name, previous_name in previous_names.items():
        current_file = getattr(instance, field_name)
        current_name = current_file.name if current_file else ""

        if previous_name != current_name:
            storage = sender._meta.get_field(field_name).storage
            _schedule_file_deletion(
                field_name,
                previous_name,
                storage,
                using,
            )


@receiver(post_delete, sender=Project)
def delete_project_media(sender, instance, using, **kwargs):
    for field_name in MEDIA_FIELDS:
        field_file = getattr(instance, field_name)

        if field_file:
            _schedule_file_deletion(
                field_name,
                field_file.name,
                field_file.storage,
                using,
            )
