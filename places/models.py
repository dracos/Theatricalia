import re
from django.db import models
from django.contrib.contenttypes import generic
from django.template.defaultfilters import slugify
from photos.models import Photo
from utils import int_to_base32
from fields import ApproximateDateField
from common.models import Alert
from countries.models import Country

class PlaceManager(models.Manager):
    # Crappy bounding box, need to do radial!
    def around(self, lat, lon):
        return self.get_query_set().filter(
            longitude__gte = lon - 0.1,
            longitude__lte = lon + 0.1,
            latitude__gte = lat - 0.1,
            latitude__lte = lat + 0.1
        )

class Place(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150)
    description = models.TextField(blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    address = models.CharField(blank=True, max_length=200)
    town = models.CharField(blank=True, max_length=50)
    country = models.ForeignKey(Country, blank=True, null=True)
    postcode = models.CharField(blank=True, max_length=10)
    telephone = models.CharField(blank=True, max_length=50)
    type = models.CharField(blank=True, max_length=100, choices=(('proscenium', 'Proscenium Arch'), ('thrust', 'Thrust'), ('multiple', 'Multiple'), ('other', 'Other')))
    size = models.CharField('Seats', blank=True, max_length=100)
    opening_date = ApproximateDateField(blank=True)
    url = models.URLField('URL', blank=True)
    wikipedia = models.URLField(blank=True)
    photos = generic.GenericRelation(Photo)

    objects = PlaceManager()

    alerts = generic.GenericRelation(Alert)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        out = self.get_name_display()
        if self.town and self.town not in out: out += u", " + self.town
        return out

    def save(self, **kwargs):
        name = re.sub('^(.*), (A|An|The)$(?i)', r'\2 \1', self.name.strip())
        self.slug = slugify('%s %s' % (name, self.town))
        self.name = re.sub('^(A|An|The) (.*)$(?i)', r'\2, \1', self.name.strip())
        super(Place, self).save(**kwargs)

    def get_name_display(self):
        out = self.name
        m = re.search('^(.*),\s+(A|An|The)$(?i)', out)
        if m:
            out = "%s %s" % (m.group(2), m.group(1))
        return out
    
    def id32(self):
        return int_to_base32(self.id)

    def make_url(self, name, *args):
        return (name, (self.id32(), self.slug) + args)

    @models.permalink
    def get_absolute_url(self):
        return self.make_url('place')

    @models.permalink
    def get_edit_url(self):
        return self.make_url('place-edit')

    @models.permalink
    def get_add_production_url(self):
        return self.make_url('place-production-add')

    @models.permalink
    def get_alert_add_url(self):
        return self.make_url('place-alert', 'add')

    @models.permalink
    def get_alert_remove_url(self):
        return self.make_url('place-alert', 'remove')

    def get_past_url(self):
        return '%s/past' % self.get_absolute_url()

    def get_future_url(self):
        return '%s/future' % self.get_absolute_url()

    def get_feed_url(self):
        return '%s/feed' % self.get_absolute_url()

    @models.permalink
    def get_productions_url(self):
        return self.make_url('place-productions')

def first_letters():
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute('SELECT DISTINCT SUBSTRING(name, 1, 1) FROM places_place')
    return cursor.fetchall()

