from app.models import Profile, Question, Answer
from .frontend_models import CardFeed, CardMain, CardAnswer, BadgeTag, ProfileCard

from django.core.paginator import Paginator
from django.db.models import Count

class BaseFeed():
    """
    This is a class for main content of the page.
    """
    pass

class PaginatedFeed(BaseFeed):
    """
    This is a class is used for pagination of the cards.

    It is used in views to create pages of explore and answer cards.
    """

    def __init__(self, pages: Paginator = None):
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

class ProfileFeed(BaseFeed):
    """
    This feed is used for rendering profile template.
    """

    def __init__(self, profile_id: int):
        # Get profile from db
        self.profile_obj = None
        try:
            self.profile_obj = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            pass
        
        # Create ProfileCard object
        self.profile = ProfileCard(self.profile_obj) if self.profile_obj else None
