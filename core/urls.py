from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("special-thanks/", views.special_thanks, name="special_thanks"),
    path("health/", views.health, name="health"),
]
