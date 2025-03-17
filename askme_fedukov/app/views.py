from django.shortcuts import render
from .models import CardFeed, CardMain, CardAnswer


def index(request):
    feed = {CardFeed(), CardFeed()}
    data = {"authenticated": True, "MAIN_COL": "8", "feed": feed}
    return render(request, "index.html", context=data)


def question(request):
    main = CardMain()
    answers = [CardAnswer(), CardAnswer()]
    data = {"authenticated": True, "main":main, "answers":answers}
    return render(request, "question.html", context=data)


def tag(request):
    return render(request, "tag.html")


def ask(request):
    return render(request, "ask.html")


def login(request):
    return render(request, "login.html")


def signup(request):
    return render(request, "signup.html")


def settings(request):
    return render(request, "settings.html")
