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

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "title",
                    "slug",
                    "short_description",
                    "description",
                    "role",
                    "technologies",
                )
            },
        ),
        (
            "Media",
            {
                "fields": (
                    "thumbnail",
                    "report",
                )
            },
        ),
        (
            "Links",
            {
                "fields": (
                    "repository_url",
                    "live_url",
                    "demo_url",
                    "demo_description",
                )
            },
        ),
        (
            "Publishing",
            {
                "fields": (
                    "status",
                    "featured",
                    "display_order",
                    "created_at",
                )
            },
        ),
    )
