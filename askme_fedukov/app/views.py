from django.shortcuts import render
from django.http import Http404
from .utils import Feed, Context, Authentication
from django.shortcuts import redirect


# Context structure
# "authenticated": True     - Show the own profile in header
# "MAIN_COL": "8"           - Number of bootstrap col for main block
#                           - (up to 9, 3 is already for tags and members aside)
# "MAIN_BORDER": "0"        - Number of bootstrap border for main block
# "ctx": Context()          - Context class for the main block. See utils.py

# ... each page could have its own context
# "main": CardMain()          - Main question card

def index(request):
    # Create pages of new questions
    page_number = request.GET.get('page', 1)
    feed = Feed.get_explore(page_number)
    
    # Check if user is authenticated
    auth = Authentication(True)

    # Create context for the page
    data = {"ctx": Context(auth, feed, "AskPupkin")}

    return render(request, "index.html", context=data)


def hot(request):
    # Create pages of hot questions
    page_number = request.GET.get('page', 1)
    feed = Feed.get_hot(page_number)
    
    # Check if user is authenticated
    auth = Authentication(True)
    
    # Create context for the page
    data = {"ctx": Context(auth, feed, title="Hot questions")}
    return render(request, "hot.html", context=data)


def question(request, id):
    # Get question by id
    try:
        main = Feed.get_question(id)
    except Feed.Question_DoesNotExist:
        raise Http404("Question not found")
    
    # Create pages of answers to the question
    page_number = request.GET.get('page', 1)
    answers = Feed.get_answers(id, page_number)
    
    # Check if user is authenticated
    auth = Authentication(True)

    # Create context for the page
    data = {"ctx": Context(auth, answers, title=main.header)}
    data["ctx"].main = main

    return render(request, "question.html", context=data)


def tag(request, name):
    # Create pages of questions by tag
    page_number = request.GET.get('page', 1)
    feed = Feed.get_questions_by_tag(name, page_number)
    
    # Check if user is authenticated
    auth = Authentication(True)
    
    # Create context for the page
    data = {"ctx": Context(auth, feed, title=f'"{name}" questions')}
    data["ctx"].tag_name = name

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

def profile(request):
    # TODO: Create profile html
    data = {"MAIN_BORDER": "0", "MAIN_COL": "9"}
    return render(request, "profile.html", context=data)