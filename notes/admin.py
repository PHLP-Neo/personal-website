from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
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
