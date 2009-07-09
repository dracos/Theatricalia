from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
	user = models.ForeignKey(User, unique=True)
	biography = models.TextField(blank=True)  
	url = models.URLField(blank=True, verify_exists=False)
	email_validated = models.BooleanField()
