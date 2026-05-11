from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.login_view, name="login"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login_legacy"),
    path("logout/", views.logout_view, name="logout"),
]
