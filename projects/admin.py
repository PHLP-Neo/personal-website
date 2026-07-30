from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "featured",
        "display_order",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "status",
        "featured",
    )

    search_fields = (
        "title",
        "short_description",
        "description",
        "technologies",
    )

    prepopulated_fields = {
        "slug": ("title",),
    }

    ordering = (
        "display_order",
        "-created_at",
    )
