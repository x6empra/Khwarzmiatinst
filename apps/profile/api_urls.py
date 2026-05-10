"""URL conf for /api/profile/ — JSON API (API.md §Profile)."""

from django.urls import path

from . import api

app_name = "investor_profile_api"

urlpatterns = [
    path("orders/", api.OrdersListAPIView.as_view(), name="orders"),
]
