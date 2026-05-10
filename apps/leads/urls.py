"""URL conf for /api/leads/ — see API.md §Leads."""

from django.urls import path

from . import views

app_name = "leads"

urlpatterns = [
    path("create/", views.lead_create, name="create"),
]
