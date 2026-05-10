"""URL conf for /dashboard/ — see PERMISSIONS.md §Pages."""

from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_home, name="home"),
    path("leads/", views.leads_list, name="leads"),
    path("leads/<int:pk>/", views.lead_detail, name="lead_detail"),
    path("leads/<int:pk>/status/", views.lead_status_change, name="lead_status"),
    path("leads/<int:pk>/delete/", views.lead_delete, name="lead_delete"),
    path("packages/", views.packages_list, name="packages"),
    path("users/", views.users_list, name="users"),
]
