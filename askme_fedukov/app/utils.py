from django.core.paginator import Paginator

from .forms import LoginForm
from .models import Question, Answer, Profile, Tag
from django.db.models import Count
from django.http import HttpRequest
from django.contrib import auth


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
    This is a class for tags.
    """

    def __init__(self, name: str, type: int = 0):
        self.name = name
        self.count = 0
        self.type = type
        self.bs_type = Tag.TAG_CHOICES[type][1] if type < len(Tag.TAG_CHOICES) else "primary"

    def __str__(self):
        return self.name

class Feed():
    """
    This is a class for pagination of the cards.
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
            print(profile)
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
    """
    def __init__(self, request: HttpRequest):
        if request is None:
            raise ValueError("Request cannot be None")
        
        self.authenticated = False
        self.profile = None
        self.login_form = None

        if auth.get_user(request).is_authenticated:
            self.authenticated = True
            self.profile = Profile.objects.get(user=auth.get_user(request))
        else:
            self.login_form = LoginForm(request.POST)
            user = CheckForm.check_login_form(request, self.login_form)
            if user is not None:
                self.profile = Profile.objects.get(user=user)
                self.authenticated = True
        
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
    """

    def __init__(self, auth: Authentication, feed: Feed, title: str):
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



class CheckForm:
    """
    This is a class for checking forms.
    """

    @staticmethod
    def check_form(request: HttpRequest, form):
        """
        Checks the form and returns True if valid, False otherwise.
        """
        if request.method == "POST":
            if form.is_valid():
                return True
            else:
                return False
        return False
    
    @staticmethod
    def check_login_form(request: HttpRequest, form):
        """
        Checks the login form and returns True if valid, False otherwise.
        """
        if request.method == "POST":
            if form.is_valid():
                user = auth.authenticate(request, **form.cleaned_data)
                if user is not None:
                    auth.login(request, user)
                    return user
                else:
                    form.add_error(None, "Invalid username or password")
        return None
    
    @staticmethod
    def check_registration_form(request: HttpRequest, form):
        """
        Checks the registration form and returns True if valid, False otherwise.
        """
        if request.method == "POST":
            if form.is_valid():
                profile = form.save()
                if profile:
                    user = profile.user
                    auth.login(request, user)
                    return user
                else:
                    form.add_error(None, "Cannot create user")
        return None
    
    @staticmethod
    def check_settings_form(request: HttpRequest, form):
        """
        Checks the registration form and returns True if valid, False otherwise.
        """
        if request.method == "POST":
            if form.is_valid():
                form.save(request.user.profile)
                return True
        return None