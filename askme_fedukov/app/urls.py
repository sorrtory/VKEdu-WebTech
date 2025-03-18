from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path("tag/", views.tag),
    path("question/", views.question),
    path("ask", views.ask),
    path("login", views.login),
    path("signup", views.signup),
    path("register", views.signup),
    path("settings", views.settings),
]
