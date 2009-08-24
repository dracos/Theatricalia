from datetime import date
from django.db import models
from django.utils import dateformat
from django.contrib.contenttypes import generic
from django.utils.safestring import mark_safe
from django.template.defaultfilters import slugify
from django.db.models import Max, Min
from utils import int_to_base32
from places.models import Place
from people.models import Person
from plays.models import Play
from photos.models import Photo
from fields import ApproximateDateField
from common.templatetags.prettify import prettify

def pretty_date_range(start_date, press_date, end_date):
    if not start_date:
        if not press_date:
            if not end_date:
                return 'Date unknown'
            else:
                return u'Ended %s' % end_date
        elif not end_date:
            return '%s (press night)' % dateformat.format(press_date, 'jS F Y')

    if not end_date:
        return u'Started %s' % start_date

    press = ''
    if not start_date and press_date:
        press = ' (press night)'
        start_date = press_date

    if dateformat.format(start_date, 'dmY') == dateformat.format(end_date, 'dmY'):
        date = end_date

    elif dateformat.format(start_date, 'mY') == dateformat.format(end_date, 'mY') and start_date.day and end_date.day:
        date = u'%s%s - %s' % (dateformat.format(start_date, 'jS'), press, end_date)
    elif dateformat.format(start_date, 'mY') == dateformat.format(end_date, 'mY') and start_date.day:
        date = u'%s%s - ? %s' % (dateformat.format(start_date, 'jS'), press, end_date)
    elif dateformat.format(start_date, 'mY') == dateformat.format(end_date, 'mY'):
        date = u'?%s - %s' % (press, end_date)

    elif start_date.year == end_date.year and start_date.day and end_date.month:
        date = u'%s%s - %s' % (dateformat.format(start_date, 'jS F'), press, end_date)
    elif start_date.year == end_date.year and start_date.day:
        date = u'%s%s - ? %s' % (dateformat.format(start_date, 'jS F'), press, end_date)
    elif start_date.year == end_date.year and start_date.month and end_date.month:
        date = u'%s%s - %s' % (dateformat.format(start_date, 'F'), press, end_date)
    elif start_date.year == end_date.year and start_date.month:
        date = u'%s%s - ? %s' % (dateformat.format(start_date, 'F'), press, end_date)
    elif start_date.year == end_date.year:
        date = u'?%s - %s' % (press, end_date)

    elif start_date.day:
        date = u'%s%s - %s' % (dateformat.format(start_date, 'jS F Y'), press, end_date)
    else:
        date = u'%s%s - %s' % (start_date, press, end_date)
    return date

class ProductionCompany(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'production companies'

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        self.slug = slugify(self.name)
        super(ProductionCompany, self).save(**kwargs)

class Production(models.Model):
    play = models.ForeignKey(Play, related_name='productions')
    company = models.ForeignKey(ProductionCompany, related_name='productions', blank=True, null=True)
    places = models.ManyToManyField(Place, through='Place', related_name='productions', blank=True)
    parts = models.ManyToManyField(Person, through='Part', related_name='productions', blank=True)
    photos = generic.GenericRelation(Photo)
    description = models.TextField(blank=True)

    def url_components(self, name):
        return (name, (), {
            'play': self.play.slug,
            'play_id': int_to_base32(self.play.id),
            'production_id': int_to_base32(self.id),
        })

    @models.permalink
    def get_absolute_url(self):
        return self.url_components('production')

    @models.permalink
    def get_edit_url(self):
        return self.url_components('production-edit')

    @models.permalink
    def get_edit_cast_url(self):
        return self.url_components('production-edit-cast')

    def __unicode__(self):
        producer = ''
        if self.company:
            producer = "%s " % self.company
        if self.places.count()>1:
            places = 'On tour, '
        elif self.places.count()==1:
            places = '%s, ' % self.places.all()[0]
        else:
            places = ''
        return "%sproduction of %s, %s%s" % (producer, self.play, places, self.date_summary())

    # Find min/max dates from the places of this production
    def get_min_max_dates(self):
        start_date = None
        end_date = None
        press_date = None
        for place in self.place_set.all():
            if not start_date or place.start_date < start_date: start_date = place.start_date
            if not press_date or place.press_date < press_date: press_date = place.press_date
            if not   end_date or place.end_date   >   end_date:   end_date = place.end_date
        return start_date, press_date, end_date

    def date_summary(self):
        return pretty_date_range(*self.get_min_max_dates())

    def started(self):
        start_date, press_date, end_date = self.get_min_max_dates()
        if start_date and start_date <= date.today():
            return True
        if press_date and press_date <= date.today():
            return True
        return False

    def finished(self):
        start_date, press_date, end_date = self.get_min_max_dates()
        if end_date and end_date < date.today():
            return True
        return False

    def place_summary(self):
        if self.places.count()>1:
            place = 'On tour'
        elif self.places.count()==1:
            place = self.places.all()[0]
        else:
            place = 'Unknown location'
        return place
        
    def title(self):
        return self.company or ''

#class Performance(models.Model):
#    production = models.ForeignKey(Production)
#    date = models.DateField()
#    time = models.TimeField(blank=True, null=True)
#    duration = models.IntegerField(blank=True, null=True)
#    place = models.ForeignKey(Place)
#
#    def __unicode__(self):
#        return '%s %s performance of %s at %s' % (self.date, self.time, self.production, self.place)

class Place(models.Model):
    production = models.ForeignKey(Production)
    place = models.ForeignKey(Place)
    start_date = ApproximateDateField(blank=True)
    press_date = models.DateField(blank=True, null=True)
    end_date = ApproximateDateField(blank=True)

    def __unicode__(self):
        return "The part of production %d at %s, %s" % (self.production.id, self.place, self.date_summary())

    def date_summary(self):
        return pretty_date_range(self.start_date, self.press_date, self.end_date)

class PartManager(models.Manager):
    def search(self, search):
        return self.get_query_set().filter(role__icontains=search).order_by('-IFNULL(productions_place.press_date, IF(productions_place.end_date!="", productions_place.end_date, productions_place.start_date))', 'production__place__press_date')

class Part(models.Model):
    production = models.ForeignKey(Production)
    person = models.ForeignKey(Person)
    role = models.CharField(max_length=100, blank=True)
    cast = models.NullBooleanField(null=True, blank=True, verbose_name='Cast/Crew')
    credited_as = models.CharField(max_length=100, blank=True)
    order = models.IntegerField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    objects = PartManager()

    def role_or_unknown(self):
        return self.role or 'Unknown'

    def __unicode__(self):
        return '%s, %s in %s' % (self.person, self.role, self.production)

    def cast_string(self):
        if self.cast == 1:
            return 'Cast'
        elif self.cast == 0:
            return 'Crew'
        else:
            return 'Unknown'
