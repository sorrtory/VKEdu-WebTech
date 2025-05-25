# This file describes frontend classes.
# They are used in templates for getting layout data.

from app.models import Answer, Profile, Tag
from app.utils.authentication import Authentication

LOREM = '''Lorem Ipsum is simply dummy text of the printing and typesetting
industry. Lorem Ipsum has been the industry's standard dummy text ever since 
the 1500s, when an unknown printer took a galley of type and scrambled it to 
make a type specimen book. It has survived not only five centuries, but also 
the leap into electronic typesetting, remaining essentially unchanged. It was 
popularised in the 1960s with the release of Letraset sheets containing Lorem 
Ipsum passages, and more recently with desktop publishing software like Aldus 
PageMaker including versions of Lorem Ipsum.'''


class BadgeTag:
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


class CardBase:
    """
    This is the frontend base class for all cards.
    """

    def __init__(
        self,
        auth: Authentication,
        card_type: str,
        id: int,
        author: Profile,
        like_status: int,
        header: str = None,
        text: str = None,
        tags: list[BadgeTag] = None,
        likes: int = 0
    ):
        self.auth = auth        # Authentication object of a viewer
        self.type = card_type   # explore / main / answer
        # Explore cards are placed on index.html like a list of cards.
        # Main cards are on question.html. In fact, the first and largest one
        # Answer cards are below the main cards on question.html

        self.author = author    # Author of the card
        self.id = id            # (Question.id, Answer.id, etc.)
        self.tags = tags        # List of tags associated with the card
        self.likes = likes      # Number of likes on the card, used for like buttons

        # Card's content
        self.header = "LOREM IPSUM" if header is None else header
        self.text = LOREM if text is None else text

        # Card layout settings
        self.AVATAR_SIZE = "2"            # col-{{AVATAR_SIZE}}
        self.CARD_BORDER = "1"            # border-{{CARD_BORDER}}

        # Like buttons' layout
        self.BTN_LIKE_SIZE = "1.5em"      # size of like button
        self.LIKE_VALUE_SIZE = "5"        # h{{LIKELABEL_SIZE}}
        self.BTN_LIKE_WRAP = "flex-wrap flex-md-nowrap"
        self.BTN_LIKE_COL = "col-2"

        # Disable button
        self.BTN_LIKE_DISABLED = None     # "disabled" / None
        self.BTN_DISLIKE_DISABLED = None  # "disabled" / None

        # Change color of button
        self.BTN_LIKE_COLOR = ""          # success/danger
        self.BTN_DISLIKE_COLOR = ""       # success/danger

        # Change icon of button
        self.BTN_LIKE_FILL = ""           # "-fill" / ""
        self.BTN_DISLIKE_FILL = ""        # "-fill" / ""

        self.like_status = like_status    # 0=neither / 1=like / -1=disliked
        self.update_like_layout()

    def is_own_card(self) -> bool:
        """
        Check if the card belongs to the authenticated user.

        Returns:
            bool: True if the card belongs to the user, False otherwise.
        """
        return self.auth.authenticated and self.author.id == self.auth.profile.id

    def update_like_layout(self):
        """
        Update the like button layout based on the user's like status.
        """
        if (not self.auth.authenticated) or self.is_own_card():
            # User cannot like or dislike
            self.BTN_LIKE_DISABLED = "disabled"
            self.BTN_DISLIKE_DISABLED = "disabled"
            self.BTN_LIKE_COLOR = "muted"
            self.BTN_DISLIKE_COLOR = "muted"
            self.BTN_LIKE_FILL = ""
            self.BTN_DISLIKE_FILL = ""
            return

        if self.like_status == 1:
            # Update like button
            self.BTN_LIKE_DISABLED = "disabled"
            self.BTN_LIKE_COLOR = "success"
            self.BTN_LIKE_FILL = "-fill"
            # Update dislike button
            self.BTN_DISLIKE_DISABLED = None
            self.BTN_DISLIKE_COLOR = ""
            self.BTN_DISLIKE_FILL = ""
        elif self.like_status == -1:
            # Update dislike button
            self.BTN_DISLIKE_DISABLED = "disabled"
            self.BTN_DISLIKE_COLOR = "danger"
            self.BTN_DISLIKE_FILL = "-fill"
            # Update like button
            self.BTN_LIKE_DISABLED = None
            self.BTN_LIKE_COLOR = ""
            self.BTN_LIKE_FILL = ""
        else:
            # User has not liked or disliked the card
            self.BTN_LIKE_DISABLED = None
            self.BTN_DISLIKE_DISABLED = None
            self.BTN_LIKE_COLOR = ""
            self.BTN_DISLIKE_COLOR = ""
            self.BTN_LIKE_FILL = ""
            self.BTN_DISLIKE_FILL = ""


class CardExplore(CardBase):
    """
    Frontend class for explore cards.

    It is used to list questions on the frontend.
    """

    def __init__(
        self,
        auth: Authentication,
        id: int,
        author: Profile,
        like_status: int,
        answers: list[Answer] = None,
        header: str = None,
        text: str = None,
        tags: list = None,
        likes: int = 0
    ):
        super().__init__(auth, "explore", id, author, like_status, header, text, tags, likes)
        self.answers = answers or []
        self.answers_count = len(self.answers)


class CardMain(CardBase):
    """
    Frontend class for main question cards.
    """

    def __init__(
        self,
        auth: Authentication,
        id: int,
        author: Profile,
        like_status: int,
        header: str = None,
        text: str = None,
        tags: list = None,
        likes: int = 0
    ):
        super().__init__(auth, "main", id, author, like_status, header, text, tags, likes)
        self.AVATAR_SIZE = "3"
        self.CARD_BORDER = "0"
        self.BTN_LIKE_SIZE = "2em"
        self.LIKE_VALUE_SIZE = "3"


class CardAnswer(CardBase):
    """
    Frontend class for answer cards.
    """

    def __init__(
        self,
        auth: Authentication,
        id: int,
        author: Profile,
        like_status: int,
        text: str = None,
        tags: list = None,
        likes: int = 0
    ):
        super().__init__(auth, "answer", id, author, like_status, text=text, tags=tags, likes=likes)
        self.BTN_LIKE_SIZE = "1.6em"
        self.BTN_LIKE_COL = "col-5 col-sm-4"
        self.BTN_LIKE_WRAP = ""


class ProfileCard:
    """
    This is a class for Profile's element frontend.
    """

    def __init__(self, profile: Profile):
        self.id = profile.id
        self.username = getattr(profile.user, "username",
                                "No username available")
        self.email = getattr(profile.user, "email", "No email available")
        self.avatar = getattr(profile, "avatar", "No avatar available")
        self.bio = getattr(profile, "bio", "No bio available")

        self.questions = profile.questions
        self.answers = profile.answers
        self.tags = [BadgeTag(tag.name, tag.type)
                     for tag in profile.tags.all()]

        # Now it's not shown, but may be used in the future
        self.likes_count = profile.answer_likes.count() + profile.question_likes.count()
        self.answer_likes = profile.answer_likes
        self.question_likes = profile.question_likes

        self.nickname = getattr(profile, "nickname", None)
