from django.shortcuts import render
from django.http import Http404
from django.shortcuts import redirect

from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

from .utils import Feed, Context, Authentication, CheckForm
from .forms import ProfileForm, SettingsForm, AskForm, AnswerForm

from urllib.parse import urlencode, urlparse, parse_qs, urlunparse

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
    feed = Feed.get_explore(page_number)

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
    feed = Feed.get_hot(page_number)

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
    main = Feed.get_question(id)
    if main is None:
        raise Http404("Question not found")

    # Check if user is authenticated
    auth = Authentication(request)

    # Create answer form
    form = AnswerForm(request.POST or None,
                      author=auth.profile, question_id=id)
    new_answer = CheckForm.check_answer_form(request, form)

    # Redirect to the question page with the new answer
    if new_answer is not None:
        page_number = Feed.get_answer_page_number_by_id(new_answer.id)
        if not page_number:
            page_number = 1
        return redirect(f"{reverse_lazy('question', kwargs={'id': id})}?page={page_number}#answer-{new_answer.id}")

    # Create pages of answers to the question
    page_number = request.GET.get('page', 1)
    answers = Feed.get_answers(id, page_number)
    
    
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
    feed = Feed.get_questions_by_tag(name, page_number)

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

    # Create context for the page
    data = {"MAIN_BORDER": "0",
            "ctx": Context(auth, None, "Ask question"),
            "form": AskForm(request.POST, request.FILES, author=auth.profile)}

    # Check for POST request
    new_qustion = CheckForm.check_ask_form(request, data["form"])
    if new_qustion:
        return redirect('question', id=new_qustion.id)

    return render(request, "ask.html", context=data)


def login(request):
    """
    Page for user login
    """

    # Check if user is authenticated
    auth = Authentication(request)
    # Set login form
    auth.set_login_form(request)

    # Redirect by continue parameter
    if auth.authenticated:
        continue_url = request.GET.get('continue')
        content = request.GET.get('content')
        if continue_url:
            # forward the content query parameter if present
            if content:
                url_parts = list(urlparse(continue_url))
                query = parse_qs(url_parts[4])
                query['content'] = content
                url_parts[4] = urlencode(query, doseq=True)
                continue_url = urlunparse(url_parts)
            return redirect(continue_url)
        else:
            return redirect('index')

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

    # Set context for the page
    data = {"MAIN_BORDER": "0", "MAIN_COL": "9",
            "ctx": Context(auth, None, "Sign up"),
            "profile_form": ProfileForm(request.POST, request.FILES)}

    # Check for POST request
    if CheckForm.check_registration_form(request, data["profile_form"]):
        if request.GET.get('continue'):
            return redirect(request.GET.get('continue'))
        else:
            return redirect('index')

    return render(request, "signup.html", context=data)


@login_required(login_url=reverse_lazy('login'), redirect_field_name='continue')
def settings(request):
    """
    Allow user to change his profile settings
    """

    # Get user profile
    auth = Authentication(request)

    # Create context
    data = {"MAIN_BORDER": "0", "MAIN_COL": "9",
            "ctx": Context(auth, None, "My profile"),
            "form": SettingsForm(request.POST, request.FILES)}
    # Set default values for the form
    data["form"].fields['username'].widget.attrs['placeholder'] = auth.profile.user.username
    data["form"].fields['email'].widget.attrs['placeholder'] = auth.profile.user.email
    data["form"].initial['avatar'] = auth.profile.avatar

    # Check for POST request
    if CheckForm.check_settings_form(request, data["form"]):
        # Redirect to the same page to show updated data
        return redirect('settings')

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
    feed = Feed()
    if feed.get_profile(id) is None:
        raise Http404("Profile not found")

    data = {"MAIN_BORDER": "0", "MAIN_COL": "9",
            "ctx": Context(auth, feed, title), }
    return render(request, "profile.html", context=data)


class CustomLogoutView(LogoutView):
    def get_redirect_url(self):
        return self.request.GET.get('continue') or super().get_redirect_url()
