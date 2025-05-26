from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
    path("hot/", views.hot, name="hot"),
    path("tag/<str:name>/", views.tag, name="tag"),
    path("question/<int:id>/", views.question, name="question"),
    path("ask/", views.ask, name="ask"),
    path("login/", views.login, name="login"),
    path("signup/", views.signup, name="signup"),
    path("register/", views.signup, name="register"),
    path("signout/", views.CustomLogoutView.as_view(), name="signout"),
    path("settings/", views.settings, name="settings"),
    path("profile/edit", views.settings),
    path("profile/<int:id>/", views.profile, name="profile"),

    # Ajax handlers
    path("like/", views.like, name="like"),
    path("correct/", views.correct, name="correct"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)