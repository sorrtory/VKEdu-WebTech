from django import forms
from .models import Profile

class LoginForm(forms.Form):
    """
    This form is used for user login.
    """
    username = forms.CharField(max_length=150, label='Username', required=False)
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    



class RegistrationForm(forms.Form):
    """
    This form is used for user registration.
    """
    username = forms.CharField(max_length=150, label='Username', required=True)
    email = forms.EmailField(label='Email', required=True)
    password1 = forms.CharField(widget=forms.PasswordInput, label='Password', required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm Password', required=True)
    # todo: add avatar field
    
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

        # Create a new user
        user = Profile.objects.create_user(username=username, email=email, password=password)
        return user
    

class ProfileForm(forms.ModelForm):
    """
    This form is used for user profile settings.
    """
    class Meta:
        model = Profile
        fields = ['avatar']
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={'multiple': False}),
        }