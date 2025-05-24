from django.core.paginator import Paginator
from django.urls import reverse_lazy

from .forms import LoginForm
from .models import Question, Answer, Profile, Tag
from django.db.models import Count
from django.http import HttpRequest
from django.contrib import auth
from urllib.parse import urlencode
from django.shortcuts import redirect
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

LOREM = '''Lorem Ipsum is simply dummy text of the printing and typesetting
industry. Lorem Ipsum has been the industry's standard dummy text ever since 
the 1500s, when an unknown printer took a galley of type and scrambled it to 
make a type specimen book. It has survived not only five centuries, but also 
the leap into electronic typesetting, remaining essentially unchanged. It was 
popularised in the 1960s with the release of Letraset sheets containing Lorem 
Ipsum passages, and more recently with desktop publishing software like Aldus 
PageMaker including versions of Lorem Ipsum.'''


class CardBase:
    """
    This is the frontend base class for all cards.
    """

    def __init__(self, card_type: str, id: int,  author: Profile,
                 header: str = None, text: str = None, tags: list[str] = None, likes: int = 0):
        self.type = card_type   # explore / main / answer
        # Explore cards example is on index.html
        # Main cards example is on question.html. In fact the largest one
        # Answer cards examples are below the main

        # Layout
        self.AVATAR_SIZE = "2"  # col-{{AVATAR_SIZE}}
        self.CARD_BORDER = "1"  # border-{{CARD_BORDER}}

        # Database
        self.author = author
        # (Question.id or Answer.id) Will be used in URL
        self.id = id

        self.header = "LOREM IPSUM" if header is None else header
        self.text = LOREM if text is None else text
        self.tags = ["tag1", "tag2"] if tags is None else tags
        self.likes = likes


class CardFeed(CardBase):
    """
    Frontend class for feed cards.
    """

    def __init__(self, id: int, author: Profile, answers: list[Answer] = None,
                 header: str = None, text: str = None, tags: list = None, likes: int = 0):
        super().__init__("explore", id, author, header, text, tags, likes)
        self.answers = answers
        self.answers_count = answers.count() if answers else 0


class CardMain(CardBase):
    """
    Frontend class for main question cards.
    """

    def __init__(self, id: int, author: Profile,
                 header: str = None, text: str = None, tags: list = None, likes: int = 0):
        super().__init__("main", id, author, header, text, tags, likes)
        self.AVATAR_SIZE = "3"
        self.CARD_BORDER = "0"


class CardAnswer(CardBase):
    """
    Frontend class for answer cards.
    """

    def __init__(self, id: int, author: Profile,
                 text: str = None, tags: list = None, likes: int = 0):
        super().__init__("answer", id, author, text=text, tags=tags, likes=likes)


class BadgeTag():
    """
    This is a class for Tag's element frontend.
    """

    def __init__(self, name: str, type: int = 0):
        self.name = name
        self.count = 0
        self.type = type
        self.bs_type = Tag.TAG_CHOICES[type][1] if type < len(
            Tag.TAG_CHOICES) else "primary"

    def __str__(self):
        return self.name


class Feed():
    """
    This is a class for pagination of the cards.

    It is used in views to create pages of cards.
    """

    def __init__(self, pages=None):
        """
        If pages are given, initializes the paginator with the given pages.

        Attributes:
            pages (Paginator): The Paginator object used for pagination.
            pages.page_range (list): The range of pages available in the paginator.
            pages.count (int): The total number of items in the paginator.
            current_page (Page): The current page object, initialized to the first page of the Paginator.
            current_page.number (int): The current page number, initialized to 1.

            profile (Profile): The Profile object of the user who created feed, sets with get_profile().
        """
        if pages is not None:
            self.pages = pages
            self.current_page = pages.page(1)

        self.profile = None

    def turn_page_to(self, page_number):
        """
        Turns the page to the specified number.
        """
        self.current_page = self.pages.get_page(page_number)

    def on_page(self, page_number):
        """
        Turns the page to the specified number and returns the current instance.
        """
        self.turn_page_to(page_number)
        return self

    @classmethod
    def get_explore(cls, page_number: int, cards_per_page: int = 3):
        """
        Returns a paginator of CardFeed objects.
        """

        questions = Question.objects.new().prefetch_related(
            'tags').annotate(like_count=Count('likes'))
        cards = [
            CardFeed(
                question.id,
                question.author,
                question.answers.all(),
                question.title,
                question.content,
                [BadgeTag(tag.name, tag.type) for tag in question.tags.all()],
                question.like_count
            )
            for question in questions
        ]
        return cls(Paginator(cards, cards_per_page)).on_page(page_number)

    @classmethod
    def get_answer_page_number_by_id(cls, id, cards_per_page: int = 3):
        """
        Returns the page number of the answer by id.
        """
        try:
            answer = Answer.objects.get(id=id)
            question = answer.question
            page_number = (question.answers.count() - 1) // cards_per_page + 1
            return page_number
        except Answer.DoesNotExist:
            return None
        except Question.DoesNotExist:
            return None

    @classmethod
    def get_answers(cls, id, page_number: int, cards_per_page: int = 3):
        """
        Returns a paginator of CardAnswer objects filtered by id.
        """
        answers = Answer.objects.filter(question_id=id).prefetch_related(
            'tags').annotate(like_count=Count('likes'))
        cards = [
            CardAnswer(
                answer.id,
                answer.author,
                answer.content,
                [BadgeTag(tag.name, tag.type) for tag in answer.tags.all()],
                answer.like_count
            )
            for answer in answers
        ]
        return cls(Paginator(cards, cards_per_page)).on_page(page_number)

    @classmethod
    def get_question(cls, id):
        """
        Returns a CardMain object by id.
        """
        try:
            question = Question.objects.get(id=id)
            card = CardMain(
                question.id,
                question.author,
                question.title,
                question.content,
                [BadgeTag(tag.name, tag.type) for tag in question.tags.all()],
                question.likes.count()
            )
            return card
        except Question.DoesNotExist:
            return None

    @classmethod
    def get_hot(cls, page_number: int, cards_per_page: int = 3):
        """
        Returns a paginator of CardMain objects.
        """
        questions = Question.objects.hot().prefetch_related(
            'tags').annotate(like_count=Count('likes'))
        cards = [
            CardFeed(
                question.id,
                question.author,
                question.answers.all(),
                question.title,
                question.content,
                [BadgeTag(tag.name, tag.type) for tag in question.tags.all()],
                question.like_count
            )
            for question in questions
        ]
        return cls(Paginator(cards, cards_per_page)).on_page(page_number)

    @classmethod
    def get_questions_by_tag(cls, tag_name: str, page_number: int, cards_per_page: int = 3):
        """
        Returns a paginator of CardFeed objects filtered by tag name.
        """
        questions = Question.objects.filter(tags__name=tag_name).prefetch_related(
            'tags').annotate(like_count=Count('likes'))
        cards = [
            CardFeed(
                question.id,
                question.author,
                question.answers.all(),
                question.title,
                question.content,
                [BadgeTag(tag.name, tag.type) for tag in question.tags.all()],
                question.like_count
            )
            for question in questions
        ]
        return cls(Paginator(cards, cards_per_page)).on_page(page_number)

    def get_profile(self, id):
        """
        Returns a Profile object by id.
        """
        try:
            profile = Profile.objects.get(id=id)
            data = {
                "id": profile.id,
                "username": profile.user.username,
                "email": profile.user.email,
                "avatar": profile.avatar.url if profile.avatar else None,
                "tags": [BadgeTag(tag.name, tag.type) for tag in profile.tags.all()],
                "questions_count": profile.questions.count(),
                "answers_count": profile.answers.count(),
            }
            self.profile = profile
            return data
        except Profile.DoesNotExist:
            return None


class Authentication:
    """
    This is a class for user session

    It is used in templates to render data related to authentication.
    """

    def __init__(self, request: HttpRequest):
        """
        Retrieves the user profile and login form from the request.

        Attributes:
            authenticated (bool): Indicates if the user is authenticated.
            profile (Profile): The Profile object of the user.
            login_form (LoginForm): The LoginForm object for user login.
        """
        if request is None:
            raise ValueError("Request cannot be None")

        self.authenticated = False
        self.profile = None
        self.login_form = None

        if auth.get_user(request).is_authenticated:
            self.authenticated = True
            self.profile = Profile.objects.get(user=auth.get_user(request))

    def setup_login_form(self, request: HttpRequest):
        self.login_form = LoginForm(request.POST or None)
        login_form_checker = CheckAuthForm(request, self.login_form)

        # Check if the form is valid and authenticate the user
        user = login_form_checker.retrieve()
        if user is not None:
            self.profile = Profile.objects.get(user=user)
            self.authenticated = True
            return login_form_checker.redirect()
        return None

    def logout(self, request: HttpRequest):
        """
        Logs out the user.
        """
        auth.logout(request)
        self.authenticated = False
        self.profile = None


class Context:
    """
    This is a class for the context of the page.

    It will be used in templates to render basic data.
    """

    def __init__(self, auth: Authentication, feed: Feed, title: str):
        """
        Initializes the class with authentication, feed, and title information.
        Attributes:
            auth (Authentication): Stores the authentication object.
            feed (Feed): Stores the feed object containing cards.
            title (str): Stores the title.
            hot_tags (list): List of hot tags, for aside block.
            best_members (list): List of best members, for aside block.
        """

        self.auth = auth
        self.feed = feed
        self.title = title
        self.hot_tags = self.get_hot_tags()
        self.best_members = self.get_best_members()

    def get_hot_tags(self):
        """
        Returns a list of hot tags.
        """
        return [BadgeTag(tag.name, tag.type) for tag in Tag.objects.get_hot_tags() if tag.name != "hot"]

    def get_best_members(self):
        """
        Returns a list of best members.
        """
        return Profile.objects.get_best_members()


class BaseCheckForm:
    """
    This is a base class for checking forms.

    It is used in views to check if the form is valid and to process it.
    """

    def __init__(self, request: HttpRequest, form):
        self.request = request
        self.form = form

    def check(self, error_msg="Invalid form data"):
        """
        Must be called before working with form.
        """
        if self.form.is_valid():
            return True
        else:
            print("add error check")
            self.form.add_error(None, error_msg)
            return False

    def save(self):
        """
        Creates a new object in the database and returns it.
        """
        if self.check():
            return self.form.save()
        return None

    def handle_post(self, handle_func=lambda: None):
        if self.request.method == "POST":
            return handle_func()

    def handle_get(self, handle_func=lambda: None):
        if self.request.method == "GET":
            return handle_func()

    def handle(self):
        self.handle_post()
        self.handle_get()

    def retrieve(self):
        """
        Save the form and return the object created in database.
        """
        return self.handle_post(self.save)

    @staticmethod
    def redirect_to(path='index', params=None, anchor="", **kwargs):
        """
        Returns a URL string for redirecting to the specified path with optional params and anchor.

        Example:
            redirect_to('question', params={'page': 2}, anchor='answer-10', id=5)
            -> '/question/5/?page=2#answer-10'
        """
        url = reverse_lazy(
            path, kwargs=kwargs) if kwargs else reverse_lazy(path)
        if params:
            if isinstance(params, dict):
                url += '?' + urlencode(params)
            elif isinstance(params, str):
                url += params if params.startswith('?') else '?' + params
        if anchor:
            url += f"#{anchor}"
        return url


class CouldContinueForm(BaseCheckForm):
    """
    Class to handle query parameters in the URL.
    It is used in views to redirect to the next URL.
    """

    def redirect(self):
        """
        Returns string redirecting to the next URL.
        """

        request = self.request
        # Redirect by "continue" parameter
        if hasattr(request, 'GET'):
            continue_url = request.GET.get('continue')
            content = request.GET.get('content')
            if continue_url:
                # forward the content query parameter if present
                # (used to keep the content of the answer form)
                # when redirecting to the question page
                if content:
                    url_parts = list(urlparse(continue_url))
                    query = parse_qs(url_parts[4])
                    query['content'] = content
                    url_parts[4] = urlencode(query, doseq=True)
                    continue_url = urlunparse(url_parts)
                return continue_url
            else:
                return 'index'


class CheckAnswerForm(BaseCheckForm):
    """
    This is a class for checking answer forms.
    """

    def __init__(self, request: HttpRequest, form):
        self.author = form.author
        self.question_id = form.question_id
        super().__init__(request, form)

    def handle_get(self):
        def handle_func():
            self.form.fields['content'].initial = self.request.GET.get(
                'content', '')
        return super().handle_get(handle_func)

    def redirect(self, answer):
        """
        Returns string redirecting to the specified answer.
        """
        page_number = Feed.get_answer_page_number_by_id(answer.id)
        if not page_number:
            page_number = 1

        return BaseCheckForm.redirect_to(
            path='question',
            params={'page': page_number},
            anchor=f"answer-{answer.id}",
            id=self.question_id
        )


class CheckAskForm(BaseCheckForm):
    """
    This is a class for checking question forms.
    """

    def __init__(self, request: HttpRequest, form):
        self.author = form.author
        super().__init__(request, form)

    def redirect(self, question):
        """
        Returns string redirecting to the specified question.
        """
        return BaseCheckForm.redirect_to(
            path='question',
            id=question.id
        )


class CheckAuthForm(CouldContinueForm):
    """
    This is a class for checking authentication forms.
    """

    def retrieve(self):
        """
        Retrieves the user from the form and logs them in.
        If the form is not valid, it adds an error to the form.
        Returns the user if successful, None otherwise.
        """
        def handle_func():
            if self.check():
                user = auth.authenticate(
                    self.request, **self.form.cleaned_data)
                if user is not None:
                    auth.login(self.request, user)
                else:
                    self.form.add_error(None, "Invalid username or password")
                return user
            return None

        return self.handle_post(handle_func)


class CheckRegistrationForm(CouldContinueForm):
    """
    This is a class for checking registration forms.
    """

    def retrieve(self):
        """
        Retrieves the user from the form and logs them in.
        If the form is not valid, it adds an error to the form.
        Returns the user if successful, None otherwise.
        """
        def handle_func():
            if self.check():
                profile = self.form.save()
                if profile:
                    user = profile.user
                    auth.login(self.request, user)
                    return user
                else:
                    self.form.add_error(None, "Cannot create user")
            return None

        return self.handle_post(handle_func)


class CheckSettingsForm(BaseCheckForm):
    """
    This is a class for checking settings forms.
    """

    def __init__(self, request: HttpRequest, form):
        self.profile = request.user.profile
        super().__init__(request, form)

    def redirect(self):
        """
        Returns string redirecting to the profile page.
        """
        return BaseCheckForm.redirect_to(
            path='profile',
            id=self.profile.id
        )
