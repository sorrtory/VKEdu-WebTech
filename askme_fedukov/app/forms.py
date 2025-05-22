from django import forms
from .models import Profile
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    """
    This form is used for user login.
    """
    username = forms.CharField(max_length=150, label='Username', required=False)
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    
class ProfileForm(forms.Form):
    """
    This form is used for user registration.
    """
    username = forms.CharField(max_length=10, label='Login', required=True)
    email = forms.EmailField(label='Email', required=True)
    avatar = forms.ImageField(label='Avatar', required=False, widget=forms.ClearableFileInput(attrs={'multiple': False}))
    password1 = forms.CharField(widget=forms.PasswordInput, label='Password', required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, label='Repeat password', required=True)
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data
    
    def save(self):
        """
        Save the user to the database.
        """
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        password = self.cleaned_data['password1']
        avatar = self.cleaned_data['avatar']
        # Create a new user
        user = Profile.objects.create_user(username=username, email=email, password=password, avatar=avatar)
        return user

from string import Template
from django.utils.safestring import mark_safe
from django.forms import ImageField
import re

class PictureWidget(forms.ClearableFileInput):
    def render(self, name, value, attrs=None, renderer=None):
        if not attrs:
            attrs = {}
        input_html = super().render(name, value, attrs, renderer)
        # Remove the "clear" checkbox and label from the rendered HTML
        if hasattr(input_html, 'replace'):
            input_html = input_html.replace('<br>', '').replace('Clear', '').replace('clear', '')
            # Remove the clear checkbox and its label
            input_html = re.sub(r'<input[^>]*type="checkbox"[^>]*>.*?(<label[^>]*>.*?</label>)?', '', input_html, flags=re.DOTALL)
        img_src = f"/media/{value}" if value else "/media/avatars/default.png"
        html = f"""
        <div style="display: flex; flex-direction: column; align-items: flex-start;">
            <div style="margin-bottom: 10px;">
                <img id="preview_{name}" src="{img_src}" alt="Avatar" style="max-width: 150px; max-height: 150px; border-radius: 8px; border: 1px solid #ccc;" />
            </div>
            {input_html}
        </div>
        <script>
        (function() {{
            var input = document.getElementById('id_{name}');
            if (input) {{
                input.addEventListener('change', function(event) {{
                    var file = event.target.files[0];
                    if (file) {{
                        var reader = new FileReader();
                        reader.onload = function(e) {{
                            document.getElementById('preview_{name}').src = e.target.result;
                        }};
                        reader.readAsDataURL(file);
                    }}
                }});
            }}
        }})();
        </script>
        """
        return mark_safe(html)

class SettingsForm(forms.Form):
    """
    This form is used for user settings (profile update).
    """
    username = forms.CharField(max_length=10, label='Login', required=False)
    email = forms.EmailField(label='Email', required=False)
    avatar = forms.ImageField(label='Avatar', required=False, widget=PictureWidget(attrs={'multiple': False}))
    password1 = forms.CharField(widget=forms.PasswordInput, label='Password', required=False)
    password2 = forms.CharField(widget=forms.PasswordInput, label='Repeat password', required=False)
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        
        username = cleaned_data.get("username")
        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        
        return cleaned_data
    
    
    def save(self, profile):
        """
        Update the user's profile in the database.
        """
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        password = self.cleaned_data['password1']
        avatar = self.cleaned_data['avatar']
        
        # Update the user
        user = profile.user
        if username:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError('This username is already taken.')
            user.username = username
        if email:
            user.email = email
        if password:
            user.set_password(password)
        # Save the user
        if username or email or password:
            user.save()

        # Update the profile avatar
        if avatar:
            profile.avatar = avatar
            profile.save()
