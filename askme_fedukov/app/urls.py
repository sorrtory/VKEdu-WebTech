from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
    path("tag/", views.tag, name="tag"),
    path("question/<int:id>/", views.question, name="question"),
    path("ask", views.ask, name="ask"),
    path("login", views.login, name="login"),
    path("signup", views.signup, name="signup"),
    path("register", views.signup, name="register"),
    path("signout", views.logout, name="signout"),
    path("settings", views.settings, name="settings"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)