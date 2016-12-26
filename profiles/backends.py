from django.contrib.auth.backends import ModelBackend as DjangoModelBackend
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from profiles.models import User

class ModelBackend(DjangoModelBackend):
    def authenticate(self, username=None, password=None):
        """Case-insensitive email lookup"""
        try:
            try:
                validate_email(username)
                user = User.objects.get(email__iexact=username)
            except ValidationError:
                user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            return None
        if user.check_password(password):
            return user

