# This file contains feed classes that contains content of the page.

from app.models import Profile
from .frontend_models import ProfileCard
from .authentication import Authentication

from django.core.paginator import Paginator


class BaseFeed():
    """
    This is a class for main content of the page.
    """

    def __init__(self, viewer_auth: Authentication):
        """
        Initialize the feed viewer with authentication information.

        Args:
            viewer_auth (Authentication): The authentication object representing the viewer.
        """
        self.viewer_auth = viewer_auth


class PaginatedFeed(BaseFeed):
    """
    This is a class is used for pagination of the cards.

    It is used in views to create pages of explore and answer cards.
    """

    def __init__(self, viewer_auth: Authentication,  pages: Paginator):
        """
        If pages are given, initializes the paginator with the given pages.

        Attributes:
            viewer_auth (Authentication): The authentication object representing the viewer.
            pages (Paginator): The Paginator object used for pagination.
            pages.page_range (list): The range of pages available in the paginator.
            pages.count (int): The total number of items in the paginator.
            current_page (Page): The current page object, initialized to the first page of the Paginator.
            current_page.number (int): The current page number, initialized to 1.
        """
        super().__init__(viewer_auth)

        self.pages = pages
        self.current_page = pages.page(1)

    def turn_page_to(self, page_number: int):
        """
        Turns the page to the specified number.
        """
        self.current_page = self.pages.get_page(page_number)

    def on_page(self, page_number: int):
        """
        Turns the page to the specified number and returns the current instance.
        """
        self.turn_page_to(page_number)
        return self


class ProfileFeed(BaseFeed):
    """
    This feed is used for rendering profile template.
    """

    def __init__(self, viewer_auth: Authentication, profile_id: int):
        """
        Args:
            viewer_auth (Authentication): The authentication object representing the viewer.
            profile_id (int): The ID of the profile to be displayed.
        """

        super().__init__(viewer_auth)

        # Get profile from db
        self.profile_obj = None
        try:
            self.profile_obj = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            pass

        # Create ProfileCard object
        self.profile = \
            ProfileCard(self.profile_obj) if self.profile_obj else None
