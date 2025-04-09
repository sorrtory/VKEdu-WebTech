from django.core.paginator import Paginator
from .models import Question, Answer, Profile

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

    def __init__(self, card_type: str, author: Profile = None,
                 header: str = None, text: str = None, tags: list[str] = None, likes: int = 0):
        self.type = card_type   # explore / main / answer
        # Explore cards example is on index.html
        # Main cards example is on question.html. In fact the largest one
        # Answer cards examples are below the main
        # Layout
        self.AVATAR_SIZE = "2"  # col-{{AVATAR_SIZE}}
        self.CARD_BORDER = "1"  # border-{{CARD_BORDER}}

        # Database
        author = author

        if header is None:
            self.header = "LOREM IPSUM"
        if text is None:
            self.text = LOREM
        if tags is None:
            self.tags = []


class CardFeed(CardBase):
    """
    Frontend class for feed cards.
    """

    def __init__(self, author: Profile = None, header: str = None, text: str = None, tags: list = None, likes: int = 0):
        super().__init__("explore", author, header, text, tags, likes)


class CardMain(CardBase):
    """
    Frontend class for main question cards.
    """

    def __init__(self):
        super().__init__("main")
        self.AVATAR_SIZE = "3"
        self.CARD_BORDER = "0"


class CardAnswer(CardBase):
    def __init__(self):
        super().__init__("answer")


class Feed():
    def __init__(self):
        pass

    @staticmethod
    def get_feed(self):
        """
        Returns a list of CardFeed objects.
        """
        cards = Question.objects.new().all()
        return [CardFeed(card.author, 
                         card.title, 
                         card.content, 
                         list(card.tags.values_list('name', flat=True)), 
                         card.likes.count()) 
                for card in cards]


def get_pagination(objects, items_per_page: int = 3):
    """
    Returns a Paginator object with 3 items per page.
    """
    return Paginator
