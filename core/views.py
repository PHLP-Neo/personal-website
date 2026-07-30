from django.shortcuts import render
from django.http import JsonResponse

from projects.models import Project


def home(request):
    featured_projects = Project.objects.filter(
        featured=True,
    )[:3]

    return render(
        request,
        "core/home.html",
        {
            "featured_projects": featured_projects,
        },
    )


def about(request):
    return render(request, "core/about.html")


def health(request):
    return JsonResponse(
        {
            "status": "ok",
        }
    )
