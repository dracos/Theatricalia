from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.ForeignKey(User, unique=True)
    biography = models.TextField(blank=True)  
    url = models.URLField('Website', blank=True, verify_exists=False)
    email_validated = models.BooleanField()
    last_alert_sent = models.DateTimeField(auto_now_add=True)

    @models.permalink
    def get_absolute_url(self):
        return ('profile', (self.user.username.lower(),))

    @models.permalink
    def get_edit_url(self):
        return ('profile-edit', ())

    @models.permalink
    def get_alert_remove_url(self):
        return ('profile-alert', ())
