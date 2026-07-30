from django.shortcuts import get_object_or_404, render

from .models import Post


def post_list(request):
    posts = Post.objects.filter(
        published=True,
    )

    return render(
        request,
        "notes/post_list.html",
        {
            "posts": posts,
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
