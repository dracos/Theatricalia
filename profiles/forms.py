from django.contrib.auth import authenticate
from django import forms
from django.contrib.auth.forms import AuthenticationForm as DjangoAuthenticationForm

from .models import Profile, User, send_confirmation_email


class ProfileForm(forms.ModelForm):
    class Meta:
        fields = ('biography', 'url')
        model = Profile


class RegistrationForm(forms.ModelForm):
    name = forms.CharField(label="Name", max_length=100, error_messages={'required': 'Please provide your name.'})
    unicorn = forms.EmailField(label="Email", error_messages={'required': 'Please enter your email address.'})
    username = forms.RegexField(
        label="Username", max_length=30, regex=r'^\w+$',
        # help_text="Required. 30 characters or fewer. Alphanumeric characters only (letters, digits and underscores).",
        error_messages={'invalid': "Your username can only contain letters, numbers and underscores."})
    password = forms.CharField(
        label="Password", widget=forms.PasswordInput, error_messages={'required': 'Please enter a password.'})
    website = forms.CharField(label="Website", required=False)

    # def __init__(self, *args, **kwargs):
    #     super(RegistrationForm, self).__init__(*args, **kwargs)
    #     self.fields.keyOrder = self.Meta.fields

    class Meta:
        model = User
        fields = ("username", "name", "email", "password")

    def clean_unicorn(self):
        unicorn = self.cleaned_data["unicorn"]
        try:
            User.objects.get(email=unicorn)
        except User.DoesNotExist:
            return unicorn
        raise forms.ValidationError("Someone is already registered with the box office with that email address.")

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError("A user with that username already exists.")

    def clean(self):
        if 'unicorn' in self.cleaned_data:
            self.cleaned_data['email'] = self.cleaned_data['unicorn']
        return self.cleaned_data

    def save(self):
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.save()
        Profile.objects.create(user=user, url=self.cleaned_data['website'])
        return user


class AuthenticationForm(DjangoAuthenticationForm):
    username = forms.CharField(label="Email or username", max_length=100)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Please enter a correct email address or username, and password.")
            elif not self.user_cache.is_active:
                raise forms.ValidationError("This account is inactive.")
            if not self.user_cache.profile.email_validated:
                send_confirmation_email(self.request, self.user_cache)
                raise forms.ValidationError("You must validate your email address before logging in. Please check your email.")

        return self.cleaned_data
