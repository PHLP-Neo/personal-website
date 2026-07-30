from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("notes/", views.notes, name="notes"),
    path("contact/", views.contact, name="contact"),
]
