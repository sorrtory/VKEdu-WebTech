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
                        get_question_by_id, get_questions_by_tag,
                        get_questions_by_text, get_json_data_from_request)
from .utils.set import Like, Correct
from .forms import ProfileForm, SettingsForm, AskForm, AnswerForm
from .utils import redirect_to
from .utils.notification import CentrifugoQuestion, CentrifugoMain

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
    
    
    return auth.responce_with_cookies(render(request, "index.html", context=data))


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
    return auth.responce_with_cookies(render(request, "hot.html", context=data))


def question(request, id):
    """
    Page with a single main question with answers.
    It also has a form to add a new answer.
    It also has a notification channel for new answers.
    """

    # Check if user is authenticated and set the session
    auth = Authentication(request)
    notification = CentrifugoQuestion(id)

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

    # If it is a successful POST request
    new_answer = form_checker.retrieve()
    if new_answer is not None:
        # Notify everyone on the question's page about the new answer
        link_to_new_answer = form_checker.redirect(new_answer)
        notification.data["link_to_new_answer"] = link_to_new_answer
        notification.publish_answer(new_answer)
        return redirect(link_to_new_answer)

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

    # Set Centrifugo cookies with subscribtion params
    # This allows to receive notifications about new answers
    notification.sub_by_cookies(auth)
    return auth.responce_with_cookies(render(request, "question.html", context=data))


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

    return auth.responce_with_cookies(render(request, "tag.html", context=data))


@require_POST
def search(request):
    """
    Search for questions by query.
    It is used by the search form in the header.
    Responses with the search results.
    """
    data = get_json_data_from_request(request)
    question_text = data.get('query', None)
    if question_text is None:
        return HttpResponseBadRequest("No query provided")

    questions = get_questions_by_text(question_text)
    if questions is None:
        return HttpResponseBadRequest("No questions found")

    return JsonResponse(
        {"results": [q.to_json() for q in questions]},
        status=200
    )


@login_required(login_url=reverse_lazy('login'), redirect_field_name='continue')
def ask_redirect(request):
    """
    Redirect to ask page. 
    Take post params "content" and "title" and to be filled into the ask form
    """
    # Pass params to ask page
    params = {}
    continue_val = request.GET.get('continue', None)
    content_val = request.POST.get('content', None)
    title_val = request.POST.get('title', None)
    if continue_val is not None:
        params['continue'] = continue_val
    if content_val is not None:
        params['content'] = content_val
    if title_val is not None:
        params['title'] = title_val

    return redirect(redirect_to('ask', params=params))


@login_required(login_url=reverse_lazy('login'), redirect_field_name='continue')
def ask(request):
    """
    Page that allows user to create a question
    """

    # Get user profile
    auth = Authentication(request)

    # Create form for asking a question
    form = AskForm(request.POST or None, author=auth.profile,
                   content=request.GET.get('content', None),
                   title=request.GET.get('title', None))
    form_checker = CheckAskForm(request, form)

    # Redirect if it is a successful POST request
    new_qustion = form_checker.retrieve()
    if new_qustion is not None:
        return redirect(form_checker.redirect(new_qustion))

    # Create context for the page
    data = {"MAIN_BORDER": "0",
            "ctx": Context(auth, None, "Ask question"),
            "form": form}

    return auth.responce_with_cookies(render(request, "ask.html", context=data))


def login(request):
    """
    Page for user login
    """
    responce = None

    # Check if user is authenticated
    auth = Authentication(request)

    # Set login form (login form is used in templates as ctx.auth.login_form)
    continue_url = auth.setup_login_form(request)
    if continue_url is not None:
        responce = redirect(continue_url)
    else:
        # Create context for the page
        data = {"MAIN_BORDER": "0", "MAIN_COL": "9",
                "ctx": Context(auth, None, "Login")}
        responce = render(request, "login.html", context=data)

    return auth.responce_with_cookies(responce)


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
        responce = redirect(form_checker.redirect())
        return auth.responce_with_cookies(auth, responce)

    # Set context for the page
    data = {"MAIN_BORDER": "0", "MAIN_COL": "9",
            "ctx": Context(auth, None, "Sign up"),
            "profile_form": form}

    return auth.responce_with_cookies(render(request, "signup.html", context=data))


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

    return auth.responce_with_cookies(render(request, "settings.html", context=data))


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
    return auth.responce_with_cookies(render(request, "profile.html", context=data))


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
    if (check := like.check_request()) is not None:
        return HttpResponseBadRequest(check)
    return JsonResponse(like.process(), status=200)


@require_POST
@login_required
def correct(request):
    """
    Process marking an answer as a correct one
    """
    auth = Authentication(request)
    id = request.GET.get('id')
    correct = Correct(
        auth,
        request,
        id
    )
    return JsonResponse(correct.process(), status=200)


class CustomLogoutView(LogoutView):
    def get_redirect_url(self):
        return self.request.GET.get('continue') or super().get_redirect_url()
