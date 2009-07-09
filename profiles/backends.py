from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend as DjangoModelBackend
from django.forms.fields import email_re

class ModelBackend(DjangoModelBackend):
    def authenticate(self, username=None, password=None):
        """Case-insensitive email lookup"""
        if email_re.search(username):
            try:
                user = User.objects.get(email__iexact=username)
            except User.DoesNotExist:
                return None
        else:
            try:
                user = User.objects.get(username__iexact=username)
            except User.DoesNotExist:
                return None
        if user.check_password(password):
            return user

