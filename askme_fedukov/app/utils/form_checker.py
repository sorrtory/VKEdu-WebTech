# This file contains classes that are used to handle forms in views.
# including checking, saving to database, and redirecting after form submission.

from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

from django.http import HttpRequest
from django.forms import BaseForm
from django.contrib import auth


from .get import get_answer_page_number_by_id
from . import redirect_to

class BaseCheckForm:
    """
    This is a base class for checking forms.

    It is used in views to check if the form is valid and to process it.
    """

    def __init__(self, request: HttpRequest, form: BaseForm):
        self.request = request
        self.form = form

    def check(self, error_msg="Invalid form data"):
        """
        Must be called before working with form.
        """
        if self.form.is_valid():
            return True
        else:
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
        """
        Return the result of handle_func if the request method is POST.
        """
        if self.request.method == "POST":
            return handle_func()

    def handle_get(self, handle_func=lambda: None):
        """
        Return the result of handle_func if the request method is GET.
        """
        if self.request.method == "GET":
            return handle_func()

    def handle(self):
        """
        Handle both GET and POST requests.
        """
        self.handle_post()
        self.handle_get()

    def retrieve(self):
        """
        Save the form and return the object created in database.
        """
        return self.handle_post(self.save)


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

    def __init__(self, request: HttpRequest, form: BaseForm):
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
        page_number = get_answer_page_number_by_id(answer.id)
        if not page_number:
            page_number = 1

        return redirect_to(
            path='question',
            params={'page': page_number},
            anchor=f"answer-{answer.id}",
            id=self.question_id
        )


class CheckAskForm(BaseCheckForm):
    """
    This is a class for checking question forms.
    """

    def __init__(self, request: HttpRequest, form: BaseForm):
        self.author = form.author
        super().__init__(request, form)

    def redirect(self, question):
        """
        Returns string redirecting to the specified question.
        """
        return redirect_to(
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

    def __init__(self, request: HttpRequest, form: BaseForm):
        self.profile = request.user.profile
        super().__init__(request, form)

    def redirect(self):
        """
        Returns string redirecting to the profile page.
        """
        return redirect_to(
            path='profile',
            id=self.profile.id
        )
