from django.http import HttpRequest
from django.contrib import auth

from app.models import Profile

from app.utils.jwt import generate_jwt_token, check_jwt_token


class Authentication:
    JWT_COOKIE_NAME = 'jwttoken'
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
            jwt_token (str): The JWT token for the user.
            request (HttpRequest): The HTTP request object.
            old_cookies (dict): Cookies from the request.
            new_cookies (dict): Cookies to be set in the response.
        """
        if request is None:
            raise ValueError("Request cannot be None")

        self.authenticated = False
        self.profile = None
        self.login_form = None
        self.jwt_token = None
        self.request = request
        self.old_cookies = request.COOKIES if request.COOKIES else {}
        self.remove_cookies = {}
        self.new_cookies = {}

        # Try to auth
        if auth.get_user(request).is_authenticated:
            self.authenticated = True
            self.profile = Profile.objects.get(user=auth.get_user(request))

            # Get JWT from cookie or generate a new one
            self.jwt_token = \
                request.COOKIES.get(Authentication.JWT_COOKIE_NAME, None)
            if self.jwt_token is None or not check_jwt_token(request, Authentication.JWT_COOKIE_NAME):
                self.jwt_token = generate_jwt_token(str(self.profile.user.id))
                self.new_cookies.update({
                    Authentication.JWT_COOKIE_NAME: self.jwt_token
                })

        # Set up notifications
        self.sub()
        self.clean_cookies()

    def sub(self):
        """
        Subscribe to the main Centrifugo channel using the user's cookies.
        """
        from app.utils.notification import CentrifugoMain
        self.notification = CentrifugoMain()
        self.notification.sub_by_cookies(self)
    
    def clean_cookies(self):
        """
        Clear the new_cookies dictionary.
        This is used to reset cookies before setting new ones.
        """
        if self.old_cookies.get("centrifugo_channel_question") and not self.request.path.startswith("/question/"):
            self.remove_cookies["centrifugo_channel_question"] = True

    def responce_with_cookies(self, response):
        """
        Set cookies from .new_cookies to the response and return it
        """
        for cookie_name, cookie_value in self.new_cookies.items():
            response.set_cookie(cookie_name, cookie_value)
        
        for cookie_name in self.remove_cookies:
            response.delete_cookie(cookie_name)
            
        return response

    def setup_login_form(self, request: HttpRequest):
        """
        Create a login form and check if the user can log in.
        """
        # Can be used in pop ups instead of full login page
        from app.utils.form_checker import CheckAuthForm
        from app.forms import LoginForm

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
