from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

class User(AbstractUser):
    name = models.CharField(_('name'), max_length=100)

class Profile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, unique=True)
    biography = models.TextField(blank=True)  
    url = models.URLField('Website', blank=True)
    email_validated = models.BooleanField()
    last_alert_sent = models.DateTimeField(auto_now_add=True)

    @models.permalink
    def get_absolute_url(self):
        return ('profile', (self.user.username.lower(),))

    @models.permalink
    def get_edit_url(self):
        return ('profile-edit', ())
