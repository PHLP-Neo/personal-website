from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from notes.models import Post
from projects.models import Project


class StaticViewSitemap(Sitemap):
    changefreq = "monthly"

    def items(self):
        return [
            "core:home",
            "core:about",
            "projects:list",
            "notes:list",
            "contact:contact",
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        priorities = {
            "core:home": 1.0,
            "projects:list": 0.8,
            "notes:list": 0.7,
        }
        return priorities.get(item, 0.5)


class ProjectSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Project.objects.all()

    def lastmod(self, project):
        return project.updated_at


class PostSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Post.objects.filter(published=True)

    def lastmod(self, post):
        return post.updated_at
