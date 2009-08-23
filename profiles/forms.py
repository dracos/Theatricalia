from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.template import Context, loader
from django import forms
from django.contrib.auth.forms import AuthenticationForm as DjangoAuthenticationForm
from models import Profile

class RegistrationForm(forms.ModelForm):
    name = forms.CharField(label="Name", max_length=100, error_messages = {'required':'Please provide your name.'})
    email = forms.EmailField(label="Email", error_messages = {'required': 'Please enter your email address.'} )
    username = forms.RegexField(label="Username", max_length=30, regex=r'^\w+$',
        #help_text = "Required. 30 characters or fewer. Alphanumeric characters only (letters, digits and underscores).",
        error_message = "This value must contain only letters, numbers and underscores.")
    password = forms.CharField( label = "Password", widget = forms.PasswordInput,
        error_messages = {'required': 'Please enter a password.'} )
    website = forms.CharField(label = "Website", required=False)

    #def __init__(self, *args, **kwargs):
    #    super(RegistrationForm, self).__init__(*args, **kwargs)
    #    self.fields.keyOrder = self.Meta.fields

    class Meta:
        model = User
        fields = ("username", "name", "email", "password")

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError("Someone is already registered with the box office with that email address.")

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError("A user with that username already exists.")

    def save(self):
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.save()
        Profile.objects.create(user=user)
        return user

class AuthenticationForm(DjangoAuthenticationForm):
    username = forms.CharField(label="Email", max_length=100)
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Please enter a correct email and password.")
            elif not self.user_cache.is_active:
                raise forms.ValidationError("This account is inactive.")
            if not self.user_cache.get_profile().email_validated:
                raise forms.ValidationError("You must validate your email address before logging in. Check your email!")

        # TODO: determine whether this should move to its own method.
        if self.request:
            if not self.request.session.test_cookie_worked():
                raise forms.ValidationError("Your Web browser doesn't appear to have cookies enabled. Cookies are required for logging in.")

        return self.cleaned_data

