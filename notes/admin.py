from django.contrib import admin
from django.utils.html import format_html

from .models import Post, PostAttachment


class PostAttachmentInline(admin.TabularInline):
    model = PostAttachment
    extra = 1
    fields = (
        "image",
        "alt_text",
        "caption",
        "markdown_snippet",
    )
    readonly_fields = ("markdown_snippet",)

    @admin.display(description="Markdown reference")
    def markdown_snippet(self, attachment):
        if not attachment.pk or not attachment.image:
            return "Save and reopen the note to copy its Markdown reference."

        return format_html("<code>{}</code>", attachment.markdown_reference())


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = (PostAttachmentInline,)
    list_display = (
        "title",
        "published",
        "published_at",
        "updated_at",
    )

    list_filter = (
        "published",
        "published_at",
    )

    search_fields = (
        "title",
        "summary",
        "body",
    )

    prepopulated_fields = {
        "slug": ("title",),
    }

    ordering = ("-published_at",)
