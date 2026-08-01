from django.shortcuts import get_object_or_404, render

from core.pagination import paginate

from .models import Post


def post_list(request):
    posts = Post.objects.filter(
        published=True,
    )
    pagination = paginate(request, posts, per_page=9)

    return render(
        request,
        "notes/post_list.html",
        {
            "posts": pagination["page_obj"].object_list,
            **pagination,
        },
    )


def post_detail(request, slug):
    post = get_object_or_404(
        Post,
        slug=slug,
        published=True,
    )

    return render(
        request,
        "notes/post_detail.html",
        {
            "post": post,
        },
    )
