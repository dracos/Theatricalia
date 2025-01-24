from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from shortcuts import send_email
from utils import int_to_base32


class User(AbstractUser):
    name = models.CharField(_('name'), max_length=100)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    biography = models.TextField(blank=True)
    url = models.URLField('Website', blank=True)
    email_validated = models.BooleanField(default=False)
    last_alert_sent = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('profile', args=(self.user.username.lower(),))

    def get_edit_url(self):
        return reverse('profile-edit')


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.profile.email_validated)


account_activation_token = AccountActivationTokenGenerator()


def send_confirmation_email(request, user):
    send_email(
        request, "Theatricalia account confirmation",
        'registration/confirmation-email.txt',
        {
            'email': user.email,
            'uid': int_to_base32(user.id),
            'user': user,
            'token': account_activation_token.make_token(user),
            'protocol': 'http',
        }, user.email
    )
