# This file describes frontend classes for cards and tags.

from app.models import Answer, Profile, Tag


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

        # Bootsrap's badge type, use like bg-{{ tag.bs_type }}
        self.bs_type = "primary"
        if type < len(Tag.TAG_CHOICES):
            self.bs_type = Tag.TAG_CHOICES[type][1]

class ProfileCard:
    """
    This is a class for Profile's element frontend.
    """

    def __init__(self, profile: Profile):
        self.id = profile.id
        self.username = getattr(profile.user, "username", "No username available")
        self.email = getattr(profile.user, "email", "No email available")
        self.avatar = getattr(profile, "avatar", "No avatar available")
        self.bio = getattr(profile, "bio", "No bio available")

        self.questions = profile.questions
        self.answers = profile.answers
        self.tags = [BadgeTag(tag.name, tag.type) for tag in profile.tags.all()]

        # Now it's not shown, but may be used in the future
        self.likes_count = profile.answer_likes.count() + profile.question_likes.count() 
        self.answer_likes = profile.answer_likes
        self.question_likes = profile.question_likes

        self.nickname = getattr(profile, "nickname", None)
