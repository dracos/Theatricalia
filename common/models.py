from django.db import models
from django.contrib.auth.models import User

exclude = [ 'created', 'created_by', 'last_modified', 'last_modified_by' ]

class TrackedModel(models.Model):
	created = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(User, related_name='created_%(class)s_set')
	last_modified = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True
