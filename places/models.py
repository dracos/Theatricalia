from django.db import models
from django.contrib.contenttypes import generic
from photos.models import Photo
from common.models import TrackedModel

class Place(TrackedModel):
	name = models.CharField(max_length=100)
	slug = models.SlugField(unique=True, max_length=100)
	description = models.TextField(blank=True)
	latitude = models.FloatField(blank=True, null=True)
	longitude = models.FloatField(blank=True, null=True)
	type = models.CharField(blank=True, max_length=100, choices=(('proscenium', 'Proscenium Arch'), ('thrust', 'Thrust'), ('multiple', 'Multiple'), ('other', 'Other')))
	size = models.CharField(blank=True, max_length=100)
	opening_date = models.DateField(blank=True, null=True)
	url = models.URLField(blank=True)
	wikipedia = models.URLField(blank=True)
	photos = generic.GenericRelation(Photo)

	def __unicode__(self):
		return self.name

        class Meta:
		ordering = ['name']

	@models.permalink
	def get_absolute_url(self):
		return ('place', (), { 'place': self.slug })

	def get_feed_url(self):
		return '%s/feed' % self.get_absolute_url()

def first_letters():
	from django.db import connection
	cursor = connection.cursor()
	cursor.execute('SELECT DISTINCT SUBSTRING(name, 1, 1) FROM places_place')
	return cursor.fetchall()

