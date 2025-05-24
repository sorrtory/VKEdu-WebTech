from django import forms
from .models import Profile, Question, Answer, Tag
from django.contrib.auth.models import User

from django.utils.safestring import mark_safe

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

class PictureWidget(forms.FileInput): # Actually can be forms.ClearableFileInput
    """
    Custom widget for displaying an image preview and file input.
    """
    def render(self, name, value, attrs=None, renderer=None):
        if not attrs:
            attrs = {}
        input_html = super().render(name, value, attrs, renderer)
        img_src = f"/media/{value}" if value else "/media/avatars/default.png"
        html = f"""
        <div style="display: flex; flex-direction: column; align-items: flex-start;">
            <div style="margin-bottom: 10px;">
                <img id="preview_{name}" src="{img_src}" alt="Avatar" 
                     style="max-width: 150px; max-height: 150px; border-radius: 8px; border: 1px solid #ccc;" />
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
    
    def __init__(self, *args, profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.profile = profile
        self.fields['username'].widget.attrs['placeholder'] = profile.user.username
        self.fields['email'].widget.attrs['placeholder'] = profile.user.email
        self.fields['avatar'].initial = profile.avatar
        self.fields['avatar'].widget.attrs['accept'] = 'image/*'

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data
    
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def save(self):
        """
        Update the user's profile in the database.
        """
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        password = self.cleaned_data['password1']
        avatar = self.cleaned_data['avatar']
        profile = self.profile
        
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

        return profile

class AskForm(forms.ModelForm):
    """
    This form is used for asking a question.
    """
    def __init__(self, *args, author=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.author = author

    class Meta:
        model = Question
        fields = ['title', 'content', 'tags']
            
        labels = {
            'title': 'Title',
            'content': 'Content',
            'tags': 'Tags',
        }
        help_texts = {
            'title': 'Enter the title of your question.',
            'content': 'Enter the content of your question.',
            'tags': 'Select tags related to your question.',
        }
        widgets = {
            'title': forms.TextInput(attrs={'required': False, 'placeholder': 'Enter your question title'}),
            'content': forms.Textarea(attrs={'required': False, 'placeholder': 'Describe your question in detail'}),
        }
    
    # Optionally, customize the widget for better UX
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Tags',
        help_text='Select tags related to your question.',
    )

    def save(self, commit=True):
        """
        Save the question to the database.
        """
        question = super().save(commit=False)
        question.author = self.author
        
        if commit:
            question.save()
            question.tags.set(self.cleaned_data['tags'])
            self.save_m2m()
        
        return question


class AnswerForm(forms.ModelForm):
    """
    This form allows user to create an answer to the question.
    """
    
    class Meta:
        model = Answer
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'required': True, 
                                             'placeholder': 'Enter your answer here',
                                             "rows": 5,
                                             "cols": 40,
                                             "style": "width: 100%;",
                                             "class": "form-control",
                                             "help_text": "Enter your answer to the question.",
                                             }, ),
        }
       
    def __init__(self, *args, author=None, question_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.author = author
        self.question_id = question_id

    def save(self, commit=True):
        """
        Save the answer to the database.
        """
        answer = super().save(commit=False)
        answer.author = self.author
        answer.question = Question.objects.get(id=self.question_id)
        
        if commit:
            answer.save()

        return answer