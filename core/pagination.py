from django.conf import settings
from django.core.paginator import Paginator


def paginate(request, queryset, per_page):
    """Paginate a queryset and provide canonical pagination URLs."""
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(request.GET.get("page"))
    base_url = f"{settings.SITE_URL}{request.path}"

    def page_url(page_number):
        if page_number == 1:
            return base_url

        return f"{base_url}?page={page_number}"

    return {
        "page_obj": page_obj,
        "page_range": paginator.get_elided_page_range(page_obj.number),
        "canonical_url": page_url(page_obj.number),
        "pagination_previous_url": (
            page_url(page_obj.previous_page_number())
            if page_obj.has_previous()
            else ""
        ),
        "pagination_next_url": (
            page_url(page_obj.next_page_number())
            if page_obj.has_next()
            else ""
        ),
    }
