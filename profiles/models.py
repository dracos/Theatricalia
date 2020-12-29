from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


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
