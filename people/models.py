from django.db import models
from utils import int_to_base32
from django.contrib.contenttypes.fields import GenericRelation
from django.template.defaultfilters import slugify
from fields import ApproximateDateField
from photos.models import Photo
from sounds.metaphone import dm
from common.models import Alert
import reversion

class PersonManager(models.Manager):
    def get_queryset(self):
        qs = super(PersonManager, self).get_queryset()
        qs = qs.exclude(deleted=True)
        return qs

    def from_name(self, name):
        names = name.split(None, 1)
        if len(names)==2:
            first_name, last_name = names
        else:
            first_name, last_name = u'', name
        new_person = Person(first_name=first_name, last_name=last_name)
        return new_person

    def create_from_name(self, name):
        new_person = self.from_name(name)
        new_person.save()
        return new_person

class Person(models.Model):
    first_name = models.CharField(max_length=50, blank=True, verbose_name='Forenames')
    last_name = models.CharField(max_length=50)
    first_name_metaphone = models.CharField(max_length=50, editable=False)
    first_name_metaphone_alt = models.CharField(max_length=50, editable=False)
    last_name_metaphone = models.CharField(max_length=50, editable=False)
    last_name_metaphone_alt = models.CharField(max_length=50, editable=False)
    slug = models.SlugField(max_length=100)
    bio = models.TextField(blank=True, verbose_name='Biography')
    dob = ApproximateDateField(blank=True, verbose_name='Date of birth')
    died = ApproximateDateField(blank=True, verbose_name='Date of death')
    imdb = models.URLField(blank=True, verbose_name='IMDb URL')
    musicbrainz = models.URLField(blank=True, verbose_name='MusicBrainz URL', default='')
    wikipedia = models.URLField(blank=True, verbose_name='Wikipedia URL')
    openplaques = models.URLField(blank=True, verbose_name='OpenPlaques URL', default='')
    web = models.URLField(blank=True, verbose_name='Personal website')
    photos = GenericRelation(Photo)
    deleted = models.BooleanField(default=False)

    alerts = GenericRelation(Alert)
    objects = PersonManager()

    def __unicode__(self):
        if self.first_name and self.last_name:
            return u'%s %s' % (self.first_name, self.last_name)
        elif self.last_name:
            return self.last_name
        elif self.first_name:
            return self.first_name
        else:
            return u'Unknown'

    def name(self):
        return unicode(self)

    def dob_machine(self):
        return repr(self.dob)

    def died_machine(self):
        return repr(self.died)

    @property
    def id32(self):
        return int_to_base32(self.id)

    def make_url(self, name, *args):
        params = (self.id32, self.slug) + args
        return (name, params)

    @models.permalink
    def get_absolute_url(self):
        return self.make_url('person')

    @models.permalink
    def get_edit_url(self):
        return self.make_url('person-edit')

    @models.permalink
    def get_more_future_url(self):
        return self.make_url('person-productions-future')

    @models.permalink
    def get_more_past_url(self):
        return self.make_url('person-productions-past')

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name_plural = 'people'

    def save(self, **kwargs):
        self.last_name = self.last_name.replace(u'\u2019', "'") # I know, but store it like this anyway.
        self.slug = slugify(self.name())
        first_name_metaphone = dm(self.first_name)
        last_name_metaphone = dm(self.last_name)
        self.first_name_metaphone = first_name_metaphone[0]
        self.first_name_metaphone_alt = first_name_metaphone[1] or ''
        self.last_name_metaphone = last_name_metaphone[0]
        self.last_name_metaphone_alt = last_name_metaphone[1] or ''
        super(Person, self).save(**kwargs)

    _creator = None
    @property
    def creator(self):
        if self._creator is None:
            try:
                latest_version = reversion.get_for_object(self).order_by('revision__date_created')[0]
                self._creator = latest_version.revision.user
            except:
                self._creator = ''
        return self._creator

    _last_modifier = None
    @property
    def last_modifier(self):
        if self._last_modifier is None:
            try:
                latest_version = reversion.get_for_object(self).order_by('-revision__date_created')[0]
                self._last_modifier = latest_version.revision.user
            except:
                self._last_modifier = ''
        return self._last_modifier

def first_letters():
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute('SELECT DISTINCT SUBSTRING(last_name, 1, 1) FROM people_person')
    return cursor.fetchall()

