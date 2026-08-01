from django.shortcuts import get_object_or_404, render

from core.pagination import paginate

from .models import Project


def project_list(request):
    projects = Project.objects.all()
    pagination = paginate(request, projects, per_page=6)

    return render(
        request,
        "projects/project_list.html",
        {
            "projects": pagination["page_obj"].object_list,
            **pagination,
        },
    )


def project_detail(request, slug):
    project = get_object_or_404(
        Project,
        slug=slug,
    )

    return render(
        request,
        "projects/project_detail.html",
        {
            "project": project,
        },
    )
