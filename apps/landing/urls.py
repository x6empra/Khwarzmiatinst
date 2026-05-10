from django.urls import path

from . import views

app_name = "landing"

urlpatterns = [
    path("", views.landing, name="home"),
    path("robots.txt", views.robots_txt, name="robots"),
]
