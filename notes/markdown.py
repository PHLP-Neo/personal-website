import html
import re
import secrets
from urllib.parse import parse_qs, urlparse

import markdown
import nh3
from django.utils.safestring import mark_safe


YOUTUBE_DIRECTIVE = re.compile(
    r"^[ \t]*\[\[youtube:(https?://[^\]\s]+)\]\][ \t]*$",
    re.MULTILINE,
)
YOUTUBE_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")

ALLOWED_TAGS = {
    "a",
    "blockquote",
    "br",
    "code",
    "em",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "img",
    "li",
    "ol",
    "p",
    "pre",
    "strong",
    "table",
    "tbody",
    "td",
    "th",
    "thead",
    "tr",
    "ul",
}

ALLOWED_ATTRIBUTES = {
    "a": {"href", "title"},
    "code": {"class"},
    "img": {"alt", "src", "title"},
    "td": {"align"},
    "th": {"align"},
}


def _youtube_video_id(url):
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower()
    path_parts = [part for part in parsed.path.split("/") if part]

    if hostname in {"youtu.be", "www.youtu.be"} and path_parts:
        candidate = path_parts[0]
    elif hostname in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
        if parsed.path == "/watch":
            candidate = parse_qs(parsed.query).get("v", [""])[0]
        elif len(path_parts) >= 2 and path_parts[0] in {"embed", "shorts"}:
            candidate = path_parts[1]
        else:
            return ""
    else:
        return ""

    return candidate if YOUTUBE_ID.fullmatch(candidate) else ""


def _youtube_embed(video_id):
    return (
        '<div class="note-video">'
        '<iframe '
        f'src="https://www.youtube-nocookie.com/embed/{video_id}" '
        'title="YouTube video player" '
        'loading="lazy" '
        'referrerpolicy="strict-origin-when-cross-origin" '
        'allow="accelerometer; autoplay; clipboard-write; encrypted-media; '
        'gyroscope; picture-in-picture; web-share" '
        'allowfullscreen>'
        "</iframe>"
        "</div>"
    )


def render_markdown(source):
    """Render trusted features while blocking arbitrary HTML and iframes."""
    source = source or ""
    token_prefix = f"NEOYOUTUBE{secrets.token_hex(8)}"
    embeds = {}

    def replace_youtube(match):
        video_id = _youtube_video_id(match.group(1))
        if not video_id:
            return match.group(0)

        token = f"{token_prefix}{len(embeds)}END"
        embeds[token] = _youtube_embed(video_id)
        return token

    source_with_tokens = YOUTUBE_DIRECTIVE.sub(replace_youtube, source)
    escaped_source = html.escape(source_with_tokens)
    rendered = markdown.markdown(
        escaped_source,
        extensions=["fenced_code", "nl2br", "sane_lists", "tables"],
        output_format="html",
    )
    rendered = nh3.clean(
        rendered,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        url_schemes={"http", "https", "mailto"},
        link_rel="noopener noreferrer",
    )

    for token, embed in embeds.items():
        rendered = rendered.replace(f"<p>{token}</p>", embed)

    return mark_safe(rendered)
