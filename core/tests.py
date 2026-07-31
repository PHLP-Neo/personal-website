from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from notes.models import Post
from projects.models import Project


@override_settings(
    SITE_URL="https://www.phlpneo.com",
    ALLOWED_HOSTS=["testserver", "www.phlpneo.com"],
    SECURE_SSL_REDIRECT=False,
)
class SeoTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title="Test Cloud Project",
            slug="test-cloud-project",
            short_description="A test cloud project case study.",
            description="Project details.",
        )
        self.published_post = Post.objects.create(
            title="Published Note",
            slug="published-note",
            summary="A published technical note.",
            body="Published content.",
            published=True,
            published_at=timezone.now(),
        )
        self.draft_post = Post.objects.create(
            title="Draft Note",
            slug="draft-note",
            body="Draft content.",
            published=False,
            published_at=timezone.now(),
        )

    def test_home_has_descriptive_metadata_and_canonical_url(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "<title>\n        Neo Ni | Backend, Cloud &amp; Data Developer\n    </title>",
            html=True,
        )
        self.assertContains(
            response,
            '<link rel="canonical" href="https://www.phlpneo.com/">',
            html=True,
        )
        self.assertContains(response, '"@type": "Person"')
        self.assertContains(response, '"@type": "WebSite"')

    def test_project_detail_uses_project_metadata(self):
        response = self.client.get(self.project.get_absolute_url())

        self.assertContains(
            response,
            '<meta name="description" content="A test cloud project case study.">',
            html=True,
        )
        self.assertContains(
            response,
            '<meta property="og:type" content="article">',
            html=True,
        )

    def test_public_page_templates_render(self):
        public_urls = [
            reverse("core:about"),
            reverse("projects:list"),
            reverse("notes:list"),
            self.published_post.get_absolute_url(),
            reverse("contact:contact"),
        ]

        for url in public_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, '<link rel="canonical"')

    def test_robots_file_allows_public_pages_and_points_to_sitemap(self):
        response = self.client.get(reverse("robots_txt"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain")
        self.assertContains(response, "User-agent: *")
        self.assertContains(response, "Disallow: /admin/")
        self.assertContains(
            response,
            "Sitemap: https://www.phlpneo.com/sitemap.xml",
        )

    def test_sitemap_contains_public_content_but_not_drafts(self):
        response = self.client.get(
            reverse("django.contrib.sitemaps.views.sitemap"),
            secure=True,
            HTTP_HOST="www.phlpneo.com",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "https://www.phlpneo.com/projects/test-cloud-project/",
        )
        self.assertContains(
            response,
            "https://www.phlpneo.com/notes/published-note/",
        )
        self.assertNotContains(
            response,
            "https://www.phlpneo.com/notes/draft-note/",
        )
