from django.test import TestCase, override_settings
from django.urls import reverse

from .markdown import render_markdown
from .models import Post, PostAttachment


@override_settings(SITE_URL="https://www.phlpneo.com")
class PostPaginationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        for number in range(10):
            Post.objects.create(
                title=f"Post {number}",
                slug=f"post-{number}",
                body="Test body",
                published=True,
            )

    def test_first_page_contains_nine_posts(self):
        response = self.client.get(reverse("notes:list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["posts"]), 9)
        self.assertContains(response, "?page=2")
        self.assertContains(
            response,
            '<link rel="canonical" href="https://www.phlpneo.com/notes/">',
            html=True,
        )

    def test_second_page_contains_remaining_post(self):
        response = self.client.get(reverse("notes:list"), {"page": 2})

        self.assertEqual(len(response.context["posts"]), 1)
        self.assertContains(
            response,
            '<link rel="canonical" href="https://www.phlpneo.com/notes/?page=2">',
            html=True,
        )


class MarkdownRenderingTests(TestCase):
    def test_markdown_features_are_rendered(self):
        rendered = render_markdown(
            "## Heading\n\n**Bold**\n\n| A | B |\n|---|---|\n| 1 | 2 |"
        )

        self.assertIn("<h2>Heading</h2>", rendered)
        self.assertIn("<strong>Bold</strong>", rendered)
        self.assertIn("<table>", rendered)

    def test_raw_html_and_unsafe_links_are_blocked(self):
        rendered = render_markdown(
            '<script>alert("x")</script>\n\n[Unsafe](javascript:alert(1))'
        )

        self.assertNotIn("<script", rendered)
        self.assertNotIn('href="javascript:', rendered)
        self.assertIn("&lt;script&gt;", rendered)

    def test_youtube_directive_uses_privacy_enhanced_embed(self):
        rendered = render_markdown(
            "[[youtube:https://www.youtube.com/watch?v=dQw4w9WgXcQ]]"
        )

        self.assertIn(
            "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ",
            rendered,
        )
        self.assertIn('loading="lazy"', rendered)

    def test_relative_gif_and_existing_line_breaks_are_preserved(self):
        rendered = render_markdown(
            "![Demo](/media/notes/demo.gif)\n\nLine one\nLine two"
        )

        self.assertIn('src="/media/notes/demo.gif"', rendered)
        self.assertIn("Line one<br>", rendered)

    def test_arbitrary_iframe_is_not_allowed(self):
        rendered = render_markdown(
            '<iframe src="https://attacker.example"></iframe>'
        )

        self.assertNotIn("<iframe", rendered)

    def test_attachment_provides_markdown_reference(self):
        post = Post.objects.create(
            title="Attachment test",
            slug="attachment-test",
            body="Test",
        )
        attachment = PostAttachment.objects.create(
            post=post,
            image="notes/attachments/attachment-test/demo.gif",
            alt_text="Animated demonstration",
        )

        self.assertEqual(
            attachment.markdown_reference(),
            "![Animated demonstration]"
            "(/media/notes/attachments/attachment-test/demo.gif)",
        )
