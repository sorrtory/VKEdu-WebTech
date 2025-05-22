from django.shortcuts import render
from django.http import Http404
from django.shortcuts import redirect

from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

from .utils import Feed, Context, Authentication, CheckForm
from .forms import ProfileForm, SettingsForm, AskForm
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
    auth = Authentication(request)

    # Create context for the page
    data = {"ctx": Context(auth, feed, "AskPupkin")}

    return render(request, "index.html", context=data)


def hot(request):
    # Create pages of hot questions
    page_number = request.GET.get('page', 1)
    feed = Feed.get_hot(page_number)

    # Check if user is authenticated
    auth = Authentication(request)

    # Create context for the page
    data = {"ctx": Context(auth, feed, title="Hot questions")}
    return render(request, "hot.html", context=data)


def question(request, id):
    # Get question by id
    main = Feed.get_question(id)
    if main is None:
        raise Http404("Question not found")

    # Create pages of answers to the question
    page_number = request.GET.get('page', 1)
    answers = Feed.get_answers(id, page_number)

    # Check if user is authenticated
    auth = Authentication(request)

    # Create context for the page
    data = {"ctx": Context(auth, answers, title=main.header)}
    data["ctx"].main = main

    return render(request, "question.html", context=data)


def tag(request, name):
    # Create pages of questions by tag
    page_number = request.GET.get('page', 1)
    feed = Feed.get_questions_by_tag(name, page_number)

    # Check if user is authenticated
    auth = Authentication(request)

    # Create context for the page
    data = {"ctx": Context(auth, feed, title=f'"{name}" questions')}
    data["ctx"].tag_name = name

    return render(request, "tag.html", context=data)


@login_required(login_url=reverse_lazy('login'), redirect_field_name='continue')
def ask(request):
    auth = Authentication(request)
    data = {"MAIN_BORDER": "0", 
            "ctx": Context(auth, None, "Ask question"),
            "form": AskForm(request.POST, request.FILES, author=auth.profile)}
    
    new_qustion = CheckForm.check_ask_form(request, data["form"])
    if new_qustion:
        return redirect('question', id=new_qustion.id)

    return render(request, "ask.html", context=data)


def login(request):
    # Check if user is authenticated
    auth = Authentication(request)

    data = {"MAIN_BORDER": "0", "MAIN_COL": "9",
            "ctx": Context(auth, None, "Login")}

    # Redirect
    if auth.authenticated:
        if request.GET.get('continue'):
            return redirect(request.GET.get('continue'))
        else:
            return redirect('index')
    return render(request, "login.html", context=data)


def signup(request):
    auth = Authentication(request)

    data = {"MAIN_BORDER": "0", "MAIN_COL": "9",
            "ctx": Context(auth, None, "Sign up"),
            "profile_form": ProfileForm(request.POST, request.FILES)}

    if CheckForm.check_registration_form(request, data["profile_form"]):
        if request.GET.get('continue'):
            return redirect(request.GET.get('continue'))
        else:
            return redirect('index')

    return render(request, "signup.html", context=data)


@login_required(login_url=reverse_lazy('login'), redirect_field_name='continue')
def settings(request):
    auth = Authentication(request)

    # Create context
    data = {"MAIN_BORDER": "0", "MAIN_COL": "9",
        "ctx": Context(auth, None, "My profile"),
        "form": SettingsForm(request.POST, request.FILES)}
    # Set default values for the form
    data["form"].fields['username'].widget.attrs['placeholder'] = auth.profile.user.username
    data["form"].fields['email'].widget.attrs['placeholder'] = auth.profile.user.email
    data["form"].initial['avatar'] = auth.profile.avatar
    
    if CheckForm.check_settings_form(request, data["form"]):
        # Redirect to the same page to show updated data
        return redirect('settings')

    return render(request, "settings.html", context=data)


def profile(request, id):
    """
    Show user profile by id
    """
    auth = Authentication(request)

    # Redirect to own profile with id==0
    if auth.authenticated and id == 0:
        id = auth.profile.id

    # Get profile by id
    feed = Feed()
    if feed.get_profile(id) is None:
        raise Http404("Profile not found")
    
    data = {"MAIN_BORDER": "0", "MAIN_COL": "9",
            "ctx": Context(auth, feed, "Profile"), }
    return render(request, "profile.html", context=data)


class CustomLogoutView(LogoutView):
    def get_redirect_url(self):
        return self.request.GET.get('continue') or super().get_redirect_url()
