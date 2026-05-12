"""URL conf for /dashboard/ — see PERMISSIONS.md §Pages."""

from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_home, name="home"),
    path("leads", views.leads_list, name="leads_short"),
    path("leads/", views.leads_list, name="leads"),
    path("leads/new", views.lead_create, name="lead_create_short"),
    path("leads/new/", views.lead_create, name="lead_create"),
    path("leads/<int:pk>", views.lead_detail, name="lead_detail_short"),
    path("leads/<int:pk>/", views.lead_detail, name="lead_detail"),
    path("leads/<int:pk>/status", views.lead_status_change, name="lead_status_short"),
    path("leads/<int:pk>/status/", views.lead_status_change, name="lead_status"),
    path("leads/<int:pk>/delete", views.lead_delete, name="lead_delete_short"),
    path("leads/<int:pk>/delete/", views.lead_delete, name="lead_delete"),
    path("packages", views.packages_list, name="packages_short"),
    path("packages/", views.packages_list, name="packages"),
    path("packages/new", views.package_create, name="package_create_short"),
    path("packages/new/", views.package_create, name="package_create"),
    path("packages/<int:pk>/edit", views.package_edit, name="package_edit_short"),
    path("packages/<int:pk>/edit/", views.package_edit, name="package_edit"),
    path("users", views.users_list, name="users_short"),
    path("users/", views.users_list, name="users"),
]
