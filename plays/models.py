import re
#from sorl.thumbnail.fields import ImageWithThumbnailsField
from django.db import models
from people.models import Person
from django.utils.html import escape
from django.utils.safestring import mark_safe

class Play(models.Model):
	title = models.CharField(max_length=255)
	slug = models.SlugField(max_length=255, unique=True)
	authors = models.ManyToManyField(Person, related_name='plays', blank=True)
	parent = models.ForeignKey('self', related_name='children', blank=True, null=True)
	description = models.TextField(blank=True)
	url = models.URLField(blank=True, verbose_name='URL')
	wikipedia = models.URLField(blank=True)

	def __unicode__(self):
		return self.nice_title()

	def authors_str(self):
		num = self.authors.count()
		authors = map(lambda x: '<a href="%s">%s</a>' % (x.get_absolute_url(), escape(x)), self.authors.all())
		if num > 2:
			str = ', '.join(authors[:num-2]) + ', ' + ', and '.join(authors[num-2:])
		elif num == 2:
			str = ' and '.join(authors)
		elif num == 1:
			str = authors[0]
		else:
			str = 'No author'
		return mark_safe(str)
			
	def nice_title(self):
		m = re.search('^(.*),\s+(A|An|The)$(?i)', self.title)
		if m:
			return "%s %s" % (m.group(2), m.group(1))
		return self.title

	@models.permalink
	def get_absolute_url(self):
		return ('play', [self.slug])

	@models.permalink
	def get_add_url(self):
		return ('play-production-add', [self.slug])

	def get_feed_url(self):
		return '%s/feed' % self.get_absolute_url()

        class Meta:
		ordering = ['title']

def first_letters():
	from django.db import connection
	cursor = connection.cursor()
	cursor.execute('SELECT DISTINCT SUBSTRING(title, 1, 1) FROM plays_play')
	return cursor.fetchall()
