from django.db import transaction
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import Post, PostAttachment


def _remember_previous_file(instance, model, field_name, using):
    if not instance.pk:
        return

    try:
        previous = (
            model._default_manager.using(using)
            .only(field_name)
            .get(pk=instance.pk)
        )
    except model.DoesNotExist:
        return

    previous_file = getattr(previous, field_name)
    setattr(
        instance,
        f"_previous_{field_name}_name",
        previous_file.name if previous_file else "",
    )


def _schedule_file_deletion(model, field_name, name, storage, using):
    if not name:
        return

    def delete_if_unreferenced():
        lookup = {field_name: name}
        still_referenced = (
            model._default_manager.using(using).filter(**lookup).exists()
        )

        if not still_referenced:
            storage.delete(name)

    transaction.on_commit(delete_if_unreferenced, using=using)


def _delete_replaced_file(instance, model, field_name, using):
    previous_name = getattr(
        instance,
        f"_previous_{field_name}_name",
        "",
    )
    current_file = getattr(instance, field_name)
    current_name = current_file.name if current_file else ""

    if previous_name and previous_name != current_name:
        storage = model._meta.get_field(field_name).storage
        _schedule_file_deletion(
            model,
            field_name,
            previous_name,
            storage,
            using,
        )


def _delete_removed_file(instance, model, field_name, using):
    field_file = getattr(instance, field_name)

    if field_file:
        _schedule_file_deletion(
            model,
            field_name,
            field_file.name,
            field_file.storage,
            using,
        )


@receiver(pre_save, sender=Post)
def remember_previous_post_image(sender, instance, using, **kwargs):
    _remember_previous_file(instance, sender, "image", using)


@receiver(post_save, sender=Post)
def delete_replaced_post_image(sender, instance, using, **kwargs):
    _delete_replaced_file(instance, sender, "image", using)


@receiver(post_delete, sender=Post)
def delete_post_image(sender, instance, using, **kwargs):
    _delete_removed_file(instance, sender, "image", using)


@receiver(pre_save, sender=PostAttachment)
def remember_previous_attachment_image(sender, instance, using, **kwargs):
    _remember_previous_file(instance, sender, "image", using)


@receiver(post_save, sender=PostAttachment)
def delete_replaced_attachment_image(sender, instance, using, **kwargs):
    _delete_replaced_file(instance, sender, "image", using)


@receiver(post_delete, sender=PostAttachment)
def delete_attachment_image(sender, instance, using, **kwargs):
    _delete_removed_file(instance, sender, "image", using)
