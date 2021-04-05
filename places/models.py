import re
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.template.defaultfilters import slugify
from django.urls import reverse
from photos.models import Photo
from utils import int_to_base32, base32_to_int, pretty_date_range
from fields import ApproximateDateField
from common.models import Alert
from countries.models import Country


class PlaceManager(models.Manager):
    # Crappy bounding box, need to do radial!
    def around(self, lat, lon):
        return self.get_queryset().filter(
            location__longitude__gte=lon - 0.1,
            location__longitude__lte=lon + 0.1,
            location__latitude__gte=lat - 0.1,
            location__latitude__lte=lat + 0.1
        )

    def get(self, **kwargs):
        b32 = kwargs.pop('Bid', None)
        if b32:
            kwargs['id'] = base32_to_int(b32)
        return super(PlaceManager, self).get(**kwargs)


class Place(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.PROTECT, related_name='children')
    slug = models.SlugField(max_length=150)
    description = models.TextField(blank=True)
    url = models.URLField('URL', blank=True)
    wikipedia = models.URLField(blank=True)
    photos = GenericRelation(Photo)

    objects = PlaceManager()

    alerts = GenericRelation(Alert)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self._str_with_name()

    def save(self, **kwargs):
        name = re.sub('(?i)^(.*), (A|An|The)$', r'\2 \1', self.name.strip())
        loc = self.locations.first()
        if loc:
            self.slug = slugify('%s %s' % (name, loc.town))
        else:
            self.slug = slugify(name)
        self.name = re.sub('(?i)^(A|An|The) (.*)$', r'\2, \1', self.name.strip())
        super(Place, self).save(**kwargs)

    def get_name_display(self):
        out = self.name
        m = re.search(r'(?i)^(.*),\s+(A|An|The)$', out)
        if m:
            out = "%s %s" % (m.group(2), m.group(1))
        return out

    def _str_with_name(self, name=None):
        out = name if name else self.get_name_display()
        if self.parent:
            out = '%s, %s' % (out, self.parent.get_name_display())
        loc = self.locations.first()
        if loc and loc.town and loc.town not in out:
            out += u", " + loc.town
        return out

    def name_for_date(self, date):
        if not date:
            return self._str_with_name()
        name = self.other_names.filter(start_date__lte=date, end_date__gte=date).first()
        if name:
            name = '%s (now %s)' % (name.get_name_display(), self.get_name_display())
        return self._str_with_name(name)

    @property
    def id32(self):
        return int_to_base32(self.id)

    def make_url(self, name, *args):
        return reverse(name, args=(self.id32, self.slug) + args)

    def get_absolute_url(self):
        return self.make_url('place')

    def get_edit_url(self):
        return self.make_url('place-edit')

    def get_add_production_url(self):
        return self.make_url('place-production-add')

    def get_past_url(self):
        return '%s/past' % self.get_absolute_url()

    def get_future_url(self):
        return '%s/future' % self.get_absolute_url()

    def get_feed_url(self):
        return '%s/feed' % self.get_absolute_url()

    def get_productions_url(self):
        return self.make_url('place-productions')


class LocationManager(models.Manager):
    # Crappy bounding box, need to do radial!
    def around(self, lat, lon):
        return self.get_queryset().filter(
            longitude__gte=lon - 0.1,
            longitude__lte=lon + 0.1,
            latitude__gte=lat - 0.1,
            latitude__lte=lat + 0.1
        )


class Location(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='locations')
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    address = models.CharField(blank=True, max_length=200)
    town = models.CharField(blank=True, max_length=50)
    country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.SET_NULL)
    postcode = models.CharField(blank=True, max_length=10)
    telephone = models.CharField(blank=True, max_length=50)
    type = models.CharField(
        blank=True, max_length=100, choices=(
            ('proscenium', 'Proscenium Arch'),
            ('thrust', 'Thrust'),
            ('multiple', 'Multiple'),
            ('other', 'Other')
        )
    )
    size = models.CharField('Seats', blank=True, max_length=100)
    opening_date = ApproximateDateField(blank=True)
    closing_date = ApproximateDateField(blank=True, default='')

    objects = LocationManager()

    class Meta:
        ordering = ['-opening_date']

    def __str__(self):
        place = str(self.place)
        date_range = pretty_date_range(self.opening_date, None, self.closing_date)
        return '%s (%s)' % (place, date_range)


class Name(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='other_names')
    name = models.CharField(max_length=100)
    start_date = ApproximateDateField(blank=True)
    end_date = ApproximateDateField(blank=True)

    class Meta:
        ordering = ['-end_date', '-start_date', 'name']

    def __str__(self):
        name = self.get_name_display()
        date_range = pretty_date_range(self.start_date, None, self.end_date)
        out = '%s (%s)' % (name, date_range)
        return out

    def save(self, **kwargs):
        self.name = re.sub('(?i)^(A|An|The) (.*)$', r'\2, \1', self.name.strip())
        super(Name, self).save(**kwargs)

    def get_name_display(self):
        out = self.name
        m = re.search(r'(?i)^(.*),\s+(A|An|The)$', out)
        if m:
            out = "%s %s" % (m.group(2), m.group(1))
        return out

    def get_absolute_url(self):
        return self.place.get_absolute_url()


def first_letters():
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute('SELECT DISTINCT SUBSTRING(name, 1, 1) FROM places_place')
    return cursor.fetchall()
