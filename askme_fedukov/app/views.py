from django.shortcuts import render
from django.http import Http404, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect

from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST


from .utils.context import Context
from .utils.authentication import Authentication
from .utils.feed import ProfileFeed
from .utils.form_checker import (CheckSettingsForm, CheckAnswerForm,
                                 CheckAskForm, CheckRegistrationForm)
from .utils.get import (get_feed_explore, get_feed_answers, get_feed_hot,
                        get_question_by_id, get_questions_by_tag,)

from .utils.set import Like


from .forms import ProfileForm, SettingsForm, AskForm, AnswerForm


# Layout controls for templates
# "MAIN_COL": "8"              - Number of bootstrap col for main html block
#                              - (must be <= 9, another 3 is taken by sidebar)
# "MAIN_BORDER": "0"           - Number of bootstrap border for main html block

# Context controls for templates
# "ctx": Context()             - contains page data such as auth, feed, title, etc.
#                              - "ctx" can be expanded in view handlers
# "..._form": ..._Form()       - contains form data, such as login, ask, settings, etc.
# "request_path": request.path - contains current request path, used for form actions


def index(request):
    """
    Page with recent questions
    """
    # Check if user is authenticated
    auth = Authentication(request)

    # Create pages of new questions
    page_number = request.GET.get('page', 1)
    feed = get_feed_explore(auth, page_number)

    # Create context for the page
    data = {"ctx": Context(auth, feed, "AskPupkin")}

    return render(request, "index.html", context=data)


def hot(request):
    """
    Just like /tag/hot, but has a different template.
    """

    # Check if user is authenticated
    auth = Authentication(request)

    # Create pages of hot questions
    page_number = request.GET.get('page', 1)
    feed = get_feed_hot(auth, page_number)

    # Create context for the page
    data = {"ctx": Context(auth, feed, title="Hot questions")}
    return render(request, "hot.html", context=data)


def question(request, id):
    """
    Page with a single question.
    It shows the question and all answers to it.
    It also allows to add a new answer.
    """

    # Check if user is authenticated
    auth = Authentication(request)

    # Get question by id
    main = get_question_by_id(auth, id)
    if main is None:
        raise Http404("Question not found")

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
    answers = get_feed_answers(auth, id, page_number)

    # Create context for the page
    data = {
        "ctx": Context(auth, answers, title=main.header),
        "answer_form": form,
        "request_path": request.path,
    }
    data["ctx"].main = main  # Question object

    return render(request, "question.html", context=data)


def tag(request, name):
    """
    Page with questions by tag name
    """

    # Check if user is authenticated
    auth = Authentication(request)

    # Create pages of questions by tag
    page_number = request.GET.get('page', 1)
    feed = get_questions_by_tag(auth, name, page_number)

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
    feed = ProfileFeed(auth, id)
    if feed.profile is None:
        raise Http404("Profile not found")

    data = {"MAIN_BORDER": "0", "MAIN_COL": "9",
            "ctx": Context(auth, feed, title), }
    return render(request, "profile.html", context=data)

@require_POST
@login_required
def like(request):
    """
    Process like action for a model instance

    Model types:
    - "question" for Question model
    - "answer" for Answer model
    - "profile" for Profile model. NOTE: this is not implemented yet
    """
    auth = Authentication(request)

    model_type = request.GET.get('model_type')
    id = request.GET.get('id')
    like = Like(
        auth,
        request,
        model_type=model_type,
        id=id
    )
    if (check:=like.check_request()) is not None:
        return HttpResponseBadRequest(check)

    result = like.process()
    
    return JsonResponse(result, status=200)



class CustomLogoutView(LogoutView):
    def get_redirect_url(self):
        return self.request.GET.get('continue') or super().get_redirect_url()
