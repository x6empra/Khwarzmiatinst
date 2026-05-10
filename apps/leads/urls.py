"""URL conf for /api/leads/ — see API.md §Leads."""

from django.urls import path

from . import views

app_name = "leads"

urlpatterns = [
    path("create/", views.lead_create, name="create"),
    path("", views.LeadListAPIView.as_view(), name="list"),
    path("<int:pk>/status/", views.LeadStatusUpdateAPIView.as_view(), name="status"),
    path("<int:pk>/", views.LeadDeleteAPIView.as_view(), name="delete"),
]
