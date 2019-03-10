import re
from django.db import models
from people.models import Person
#from django.utils.html import escape
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.fields import GenericRelation
from utils import int_to_base32
from common.models import Alert
from common.templatetags.prettify import prettify

class Play(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    authors = models.ManyToManyField(Person, related_name='plays', blank=True)
    parent = models.ForeignKey('self', related_name='children', blank=True, null=True, on_delete=models.SET_NULL)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True, verbose_name='URL')
    wikipedia = models.URLField(blank=True)

    alerts = GenericRelation(Alert)

    class Meta:
        ordering = ['title']

    def __unicode__(self):
        title = self.get_title_display()
        authors = ''
        if self.id:
            authors = self.get_authors_display(html=False)
        if authors:
            title += u', by ' + authors
        return title

    @property
    def id32(self):
        return int_to_base32(self.id)

    def save(self, **kwargs):
        title = self.get_title_display()
        self.slug = slugify(title)
        self.title = re.sub('^(A|An|The) (.*)$(?i)', r'\2, \1', self.title)
        super(Play, self).save(**kwargs)

    def get_title_display(self):
        return re.sub('^(.*),\s+(A|An|The)$(?i)', r'\2 \1', self.title)

    def get_authors_display(self, html=True):
        num = self.authors.count()
        if html:
            authors = map(lambda x: u'<span itemprop="author" itemscope itemtype="http://schema.org/Person"><a itemprop="url" href="%s">%s</a></span>' % (x.get_absolute_url(), prettify(x)), self.authors.all())
        else:
            authors = [ unicode(x) for x in self.authors.all() ]
        if num > 2:
            str = u', '.join(authors[:num-2]) + u', ' + u', and '.join(authors[num-2:])
        elif num == 2:
            str = u' and '.join(authors)
        elif num == 1:
            str = authors[0]
        else:
            str = u''
        return mark_safe(str)
            
    def construct_url(self, name, *args):
        return reverse(name, args=(int_to_base32(self.id), self.slug) + args)

    def get_absolute_url(self):
        return self.construct_url('play')

    def get_past_url(self):
        return self.construct_url('play-productions-past')

    def get_future_url(self):
        return self.construct_url('play-productions-future')

    def get_add_url(self):
        return self.construct_url('play-production-add')

    def get_edit_url(self):
        return self.construct_url('play-edit')

    def get_feed_url(self):
        return '%s/feed' % self.get_absolute_url()
