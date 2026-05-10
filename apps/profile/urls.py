"""URL conf for /profile/ — HTML pages (PERMISSIONS.md §Pages)."""

from django.urls import path

from . import views

app_name = "investor_profile"

urlpatterns = [
    path("", views.overview, name="overview"),
    path("password/", views.password_change, name="password"),
    path("orders/", views.orders, name="orders"),
]
