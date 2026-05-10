"""URL conf for the public packages page (HTML)."""

from django.urls import path

from . import views

app_name = "packages"

urlpatterns = [
    path("", views.packages_page, name="list"),
]
