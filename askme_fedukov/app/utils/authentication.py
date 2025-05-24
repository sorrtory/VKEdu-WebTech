from django.http import HttpRequest
from django.contrib import auth

from app.models import Profile

from app.utils.form_checker import CheckAuthForm
from app.forms import LoginForm

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