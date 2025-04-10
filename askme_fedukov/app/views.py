from django.shortcuts import render
from . import utils

from .utils import Feed
from django.shortcuts import redirect


# Context structure
# "authenticated": True     - Show the own profile in header
# "MAIN_COL": "8"           - Number of bootstrap col for main block
#                           - (up to 9, 3 is already for tags and members aside)
# "MAIN_BORDER": "0"        - Number of bootstrap border for main block
# "title": "AskPupkin"      - Title of the page

# ... each page could have its own context
# "feed"                      - A class of cards. See utils.py
# "not_paginate": True        - Remove page navigation

def index(request):
    feed = Feed.get_feed()
    page_number = request.GET.get('page', 1)
    feed.turn_page_to(page_number)
    data = {"authenticated": True, "feed": feed, }
    return render(request, "index.html", context=data)


def question(request, id):
    main = Feed.get_question(id)
    answers = Feed.get_answers(id)
    page_number = request.GET.get('page', 1)
    answers.turn_page_to(page_number)
    data = {"main": main, "answers": answers}
    print(answers.pages.page_range)
    return render(request, "question.html", context=data)


def tag(request, name):
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


def logout(request):
    # TODO: Logout
    return redirect('index')