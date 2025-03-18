from django.shortcuts import render
from . import utils


# Context structure
# "authenticated": True     - Show the own profile in header
# "MAIN_COL": "8"           - Number of bootstrap col for main block
#                           - (up to 9, 3 is already for tags and members aside)
# "MAIN_BORDER": "0"        - Number of bootstrap border for main block
# "title": "AskPupkin"      - Title of the page

# ... each page could have its own context
# "feed"                      - A pack of cards
# "not_paginate": True        - Remove page navigation

def index(request):
    feed = {utils.CardFeed(), utils.CardFeed()}
    data = {"authenticated": True, "feed": feed}
    return render(request, "index.html", context=data)


def question(request):
    main = utils.CardMain()
    answers = [utils.CardAnswer(), utils.CardAnswer()]
    data = {"main": main, "answers": answers}
    return render(request, "question.html", context=data)


def tag(request):
    feed = {utils.CardFeed(), utils.CardFeed()}
    data = {"tag": "bender", "feed": feed}
    return render(request, "tag.html", context=data)


def ask(request):
    data = {"MAIN_BORDER": "0"}
    return render(request, "ask.html", context=data)


def login(request):
    data = {"MAIN_BORDER": "0", "MAIN_COL": "9"}
    return render(request, "login.html", context=data)


def signup(request):
    data = {"MAIN_BORDER": "0", "MAIN_COL": "9"}
    return render(request, "signup.html", context=data)


def settings(request):
    data = {"MAIN_BORDER": "0", "MAIN_COL": "9"}
    return render(request, "settings.html", context=data)
