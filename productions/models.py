from django.db import models
from django.utils import dateformat
from django.contrib.contenttypes import generic
from django.utils.safestring import mark_safe
from utils import int_to_base32
from places.models import Place
from people.models import Person
from plays.models import Play
from photos.models import Photo
from fields import ApproximateDateField
from common.templatetags.prettify import prettify

class ProductionCompany(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'production companies'

    def __unicode__(self):
        return self.name

class Production(models.Model):
    play = models.ForeignKey(Play, related_name='productions')
    company = models.ForeignKey(ProductionCompany, related_name='productions', blank=True, null=True)
    start_date = ApproximateDateField(blank=True)
    press_date = models.DateField(blank=True, null=True)
    end_date = ApproximateDateField(blank=True)
    places = models.ManyToManyField(Place, related_name='productions', blank=True)
    parts = models.ManyToManyField(Person, through='Part', related_name='productions', blank=True)
    photos = generic.GenericRelation(Photo)
    description = models.TextField(blank=True)

    @models.permalink
    def get_absolute_url(self):
        return ('production', (), {'play': self.play.slug, 'production_id': int_to_base32(self.id) } )

    @models.permalink
    def get_edit_url(self):
        return ('production-edit', (), {'play': self.play.slug, 'production_id': int_to_base32(self.id) } )

    @models.permalink
    def get_edit_cast_url(self):
        return ('production-edit-cast', (), {'play': self.play.slug, 'production_id': int_to_base32(self.id) } )

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

    def feed_title(self):
        if self.places.count()>1:
            places = 'On tour, '
        elif self.places.count()==1:
            places = '%s, ' % self.places.all()[0]
        else:
            places = ''
        return "%s, %s%s" % (self.play, places, self.date_summary())

    def date_summary(self):
        if not self.start_date:
            if not self.press_date:
                if not self.end_date:
                    return ''
                else:
                    return u'Ended %s' % dateformat.format(self.end_date, 'jS F Y')
            else:
                date = '%s (press night)' % dateformat.format(self.press_date, 'jS F Y')
                if self.end_date:
                    date += ' - %s' % self.end_date
                return mark_safe(date)

        if not self.end_date:
            return u'Started %s' % dateformat.format(self.start_date, 'jS F Y')

        if dateformat.format(self.start_date, 'dmY') == dateformat.format(self.end_date, 'dmY'):
                        date = u'%s' % dateformat.format(self.end_date, 'jS F Y')
        elif dateformat.format(self.start_date, 'mY') == dateformat.format(self.end_date, 'mY'):
                        date = u'%s - %s' % (dateformat.format(self.start_date, 'jS'), dateformat.format(self.end_date, 'jS F Y'))
        elif self.start_date.year == self.end_date.year:
                        date = u'%s - %s' % (dateformat.format(self.start_date, 'jS F'), dateformat.format(self.end_date, 'jS F Y'))
        else:
                        date = u'%s - %s' % (dateformat.format(self.start_date, 'jS F Y'), dateformat.format(self.end_date, 'jS F Y'))
        return date

    def place_summary(self):
        if self.places.count()>1:
            place = 'On tour'
        elif self.places.count()==1:
            place = self.places.all()[0]
        else:
            place = 'Unknown location'
        return place
        
    def place_list(self):
        if self.places.count()>1:
            place = []
            for p in self.places.all():
                place.append('<a href="%s">%s</a>' % (p.get_absolute_url(), p))
        elif self.places.count()==1:
            p = self.places.all()[0]
            place = '<a href="%s">%s</a>' % (p.get_absolute_url(), p)
        else:
            place = 'an unknown location'
        return place
        
    def title(self):
        return self.company or ''

class Performance(models.Model):
    production = models.ForeignKey(Production)
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    place = models.ForeignKey(Place)

    def __unicode__(self):
        return '%s %s performance of %s at %s' % (self.date, self.time, self.production, self.place)

class Part(models.Model):
    production = models.ForeignKey(Production)
    person = models.ForeignKey(Person)
    role = models.CharField(max_length=100, blank=True)
    cast = models.NullBooleanField(null=True, blank=True, verbose_name='Cast/Crew')
    credit = models.CharField(max_length=100, blank=True)
    order = models.IntegerField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    visible = models.BooleanField(default=True)

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
