from django.shortcuts import render
from django.http import Http404
from django.shortcuts import redirect

from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

from .utils.context import Context
from .utils.authentication import Authentication
from .utils.feed import PaginatedFeed, ProfileFeed
from .utils.form_checker import (CheckSettingsForm, CheckAnswerForm,
                                 CheckAskForm, CheckRegistrationForm)

from .forms import ProfileForm, SettingsForm, AskForm, AnswerForm


# Context structure
# "MAIN_COL": "8"           - Number of bootstrap col for main html block
#                           - (up to 9, 3 is already for tags and members aside)
# "MAIN_BORDER": "0"        - Number of bootstrap border for main html block
# "ctx": Context()          - Context class for the page


def index(request):
    """
    Page with recent questions
    """

    # Create pages of new questions
    page_number = request.GET.get('page', 1)
    feed = PaginatedFeed.get_explore(page_number)

    # Check if user is authenticated
    auth = Authentication(request)

    # Create context for the page
    data = {"ctx": Context(auth, feed, "AskPupkin")}

    return render(request, "index.html", context=data)


def hot(request):
    """
    Almost like /tag/hot
    """

    # Create pages of hot questions
    page_number = request.GET.get('page', 1)
    feed = PaginatedFeed.get_hot(page_number)

    # Check if user is authenticated
    auth = Authentication(request)

    # Create context for the page
    data = {"ctx": Context(auth, feed, title="Hot questions")}
    return render(request, "hot.html", context=data)


def question(request, id):
    """
    Page with a single question.
    It shows the question and all answers to it.
    It also allows to add a new answer.
    """

    # Get question by id
    main = PaginatedFeed.get_question(id)
    if main is None:
        raise Http404("Question not found")

    # Check if user is authenticated
    auth = Authentication(request)

    # Create answer form
    form = AnswerForm(request.POST or None,
                      author=auth.profile, question_id=id)
    form_checker = CheckAnswerForm(request, form)

    # Insert ?content to form
    form_checker.handle_get()

    # Redirect if it is a successful POST request
    new_answer = form_checker.retrieve()
    if new_answer is not None:
        return redirect(form_checker.redirect(new_answer))

    # Create pages of answers to the question
    page_number = request.GET.get('page', 1)
    answers = PaginatedFeed.get_answers(id, page_number)

    # Create context for the page
    data = {
        "ctx": Context(auth, answers, title=main.header),
        "answer_form": form,
        "request_path": request.path,
    }
    data["ctx"].main = main

    return render(request, "question.html", context=data)


def tag(request, name):
    """
    Page with questions by tag name
    """

    # Create pages of questions by tag
    page_number = request.GET.get('page', 1)
    feed = PaginatedFeed.get_questions_by_tag(name, page_number)

    # Check if user is authenticated
    auth = Authentication(request)

    # Create context for the page
    data = {"ctx": Context(auth, feed, title=f'"{name}" questions')}
    data["ctx"].tag_name = name

    return render(request, "tag.html", context=data)


@login_required(login_url=reverse_lazy('login'), redirect_field_name='continue')
def ask(request):
    """
    Page that allows user to create a question
    """

    # Get user profile
    auth = Authentication(request)

    # Create form for asking a question
    form = AskForm(request.POST or None, author=auth.profile)
    form_checker = CheckAskForm(request, form)

    # Redirect if it is a successful POST request
    new_qustion = form_checker.retrieve()
    if new_qustion is not None:
        # return redirect('question', id=new_qustion.id)
        return redirect(form_checker.redirect(new_qustion))

    # Create context for the page
    data = {"MAIN_BORDER": "0",
            "ctx": Context(auth, None, "Ask question"),
            "form": form}

    return render(request, "ask.html", context=data)


def login(request):
    """
    Page for user login
    """

    # Check if user is authenticated
    auth = Authentication(request)

    # Set login form (login form is used in templates as ctx.auth.login_form)
    continue_url = auth.setup_login_form(request)
    if continue_url is not None:
        return redirect(continue_url)

    # Create context for the page
    data = {"MAIN_BORDER": "0", "MAIN_COL": "9",
            "ctx": Context(auth, None, "Login")}

    return render(request, "login.html", context=data)


def signup(request):
    """
    Page for user registration
    """

    # Get user profile
    auth = Authentication(request)

    # Create form for user registration
    form = ProfileForm(request.POST or None, request.FILES or None)
    form_checker = CheckRegistrationForm(request, form)

    # Redirect if it is a successful POST request
    new_user = form_checker.retrieve()
    if new_user is not None:
        return redirect(form_checker.redirect())

    # Set context for the page
    data = {"MAIN_BORDER": "0", "MAIN_COL": "9",
            "ctx": Context(auth, None, "Sign up"),
            "profile_form": form}

    return render(request, "signup.html", context=data)


@login_required(login_url=reverse_lazy('login'), redirect_field_name='continue')
def settings(request):
    """
    Allow user to change his profile settings
    """

    # Get user profile
    auth = Authentication(request)

    # Create form for user settings
    form = SettingsForm(request.POST or None,
                        request.FILES or None, profile=auth.profile)
    form_checker = CheckSettingsForm(request, form)

    # Redirect if it is a successful POST request
    new_user = form_checker.retrieve()
    if new_user is not None:
        return redirect(form_checker.redirect())

    # Create context
    data = {"MAIN_BORDER": "0", "MAIN_COL": "9",
            "ctx": Context(auth, None, "My profile"),
            "form": form}

    return render(request, "settings.html", context=data)


def profile(request, id):
    """
    Show user profile by id
    """
    auth = Authentication(request)

    title = "Profile"
    # Redirect to own profile with id==0
    if auth.authenticated and id == 0:
        id = auth.profile.id
        title = "My profile"

    # Get profile by id
    feed = ProfileFeed(id)
    if feed.profile is None:
        raise Http404("Profile not found")

    data = {"MAIN_BORDER": "0", "MAIN_COL": "9",
            "ctx": Context(auth, feed, title), }
    return render(request, "profile.html", context=data)


class CustomLogoutView(LogoutView):
    def get_redirect_url(self):
        return self.request.GET.get('continue') or super().get_redirect_url()
