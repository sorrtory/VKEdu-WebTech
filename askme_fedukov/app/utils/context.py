from app.models import Profile, Tag
from .frontend_models import BadgeTag
from .authentication import Authentication

from .feed import BaseFeed
from .cache import CacheManager

class Context:
    """
    This is a class for the context of the page.

    It will be used in templates to render basic data.
    """

    def __init__(self, auth: Authentication, feed: BaseFeed, title: str):
        """
        Initializes the class with authentication, feed, and title information.
        Attributes:
            auth (Authentication): Stores the authentication object.
            feed (Feed): Stores the feed object containing main info.
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
        # tags = Tag.objects.get_hot_tags()
        tags = CacheManager().get("hot_tags")
        tags = tags if tags else []
        return [BadgeTag(tag.name, tag.type) for tag in tags if tag.name != "hot"]

    def get_best_members(self):
        """
        Returns a list of best members.
        """
        # best = Profile.objects.get_best_members()
        best = CacheManager().get("best_members")
        best = best if best else []
        return best
