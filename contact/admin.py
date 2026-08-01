from django.contrib import admin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        "subject",
        "name",
        "email",
        "created_at",
        "notification_sent",
        "read",
        "archived",
    )

    list_filter = (
        "read",
        "archived",
        "created_at",
    )

    search_fields = (
        "name",
        "email",
        "subject",
        "message",
    )

    readonly_fields = (
        "name",
        "email",
        "subject",
        "message",
        "created_at",
        "notification_sent_at",
        "notification_error",
    )

    ordering = ("-created_at",)

    actions = [
        "mark_as_read",
        "mark_as_unread",
        "archive_messages",
    ]

    @admin.display(boolean=True, description="Email sent")
    def notification_sent(self, message):
        return message.notification_sent_at is not None

    @admin.action(description="Mark selected messages as read")
    def mark_as_read(self, request, queryset):
        queryset.update(read=True)

    @admin.action(description="Mark selected messages as unread")
    def mark_as_unread(self, request, queryset):
        queryset.update(read=False)

    @admin.action(description="Archive selected messages")
    def archive_messages(self, request, queryset):
        queryset.update(archived=True)
