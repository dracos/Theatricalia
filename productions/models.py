from datetime import date

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.fields import GenericRelation
from django.template.defaultfilters import slugify
from reversion.models import Version

from common.models import Alert
from common.templatetags.prettify import prettify
from utils import int_to_base32, pretty_date_range
from places.models import Place as PlacePlace
from people.models import Person
from plays.models import Play
from photos.models import Photo
from fields import ApproximateDateField


class ProductionCompany(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True, verbose_name='Website')

    alerts = GenericRelation(Alert)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'production companies'

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        self.slug = slugify(self.name)
        super(ProductionCompany, self).save(**kwargs)

    @property
    def id32(self):
        return int_to_base32(self.id)

    def construct_url(self, name, *args):
        return reverse(name, args=(int_to_base32(self.id), self.slug) + args)

    def get_absolute_url(self):
        return self.construct_url('company')

    def get_edit_url(self):
        return self.construct_url('company-edit')

    def get_add_production_url(self):
        return self.construct_url('company-production-add')

    def get_past_url(self):
        return '%s/past' % self.get_absolute_url()

    def get_future_url(self):
        return '%s/future' % self.get_absolute_url()


class ProductionManager(models.Manager):
    def get_queryset(self):
        qs = super(ProductionManager, self).get_queryset()
        qs = qs.exclude(source__startswith='<a href="http://wo')  # National
        qs = qs.exclude(source__startswith='HIDE')
        # qs = qs.exclude(source__endswith='University of Bristol Theatre Collection</a>')
        # qs = qs.exclude(source__endswith='AHDS Performing Arts</a>')
        # qs = qs.exclude(source__endswith='RSC Performance Database</a>')
        return qs

    def prefetch_companies(self, productions):
        companiesM2M = Production_Companies.objects.filter(
            production__in=productions).select_related('productioncompany')
        m2m = {}
        for c in companiesM2M:
            m2m.setdefault(c.production_id, []).append(c.productioncompany)
        for p in productions:
            p._companies = m2m.get(p.id, [])

    def prefetch_places(self, productions):
        placeM2M = Place.objects.filter(production__in=productions).order_by('start_date', 'press_date', 'end_date')
        m2m = {}
        for p in placeM2M:
            m2m.setdefault(p.production_id, []).append(p)
        for p in productions:
            p._place_set = m2m.get(p.id, [])
        return placeM2M


class Production(models.Model):
    play = models.ForeignKey(Play, related_name='productions', on_delete=models.CASCADE)
    companies = models.ManyToManyField(
        ProductionCompany, through='Production_Companies', related_name='productions', blank=True)
    places = models.ManyToManyField(PlacePlace, through='Place', related_name='productions', blank=True)
    parts = models.ManyToManyField(Person, through='Part', related_name='productions', blank=True)
    photos = GenericRelation(Photo)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    seen_by = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Visit', related_name='seen', blank=True)
    source = models.TextField(blank=True)
    url = models.URLField(blank=True, verbose_name='Web page')
    book_tickets = models.URLField(blank=True, verbose_name='Booking URL')

    objects = ProductionManager()
    all_objects = models.Manager()

    @property
    def id32(self):
        return int_to_base32(self.id)

    def url_components(self, name, **kwargs):
        kwargs.update({
            'play': self.play.slug,
            'play_id': int_to_base32(self.play.id),
            'production_id': int_to_base32(self.id),
        })
        return reverse(name, kwargs=kwargs)

    def get_absolute_url(self):
        return self.url_components('production')

    def get_edit_url(self):
        return self.url_components('production-edit')

    def get_edit_cast_url(self):
        return self.url_components('production-edit-cast')

    def get_seen_url(self):
        return self.url_components('production-seen', type='add')

    def get_seen_no_url(self):
        return self.url_components('production-seen', type='remove')

    def __str__(self):
        producer = places = ''
        if self.id:
            producer = self.get_companies_display(html=False)
            if producer:
                producer += ' '

            places = self.place_summary()
            if places == 'Unknown location':
                places = ''
            else:
                places = '%s, ' % places

        return "%sproduction of %s, %s%s" % (producer, self.play, places, self.date_summary())

    _place_set = None

    def _get_place_set(self):
        if self._place_set is None:
            self._place_set = self.place_set.order_by('start_date', 'press_date', 'end_date')
        return self._place_set

    def place_set_ordered(self):
        return self._get_place_set()

    # Find min/max dates from the places of this production
    def get_min_max_dates(self):
        start_date = None
        end_date = None
        press_date = None
        for place in self._get_place_set():
            if not start_date:
                start_date = place.start_date
            if not press_date:
                press_date = place.press_date
            end_date = place.end_date
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
        places = self.place_set.all()
        count = places.count()
        if count > 2:
            place = u'%s, %s, and other locations' % (places[0].name_for_date(), places[1].name_for_date())
        elif count == 2:
            place = u'%s and %s' % (places[0].name_for_date(), places[1].name_for_date())
        elif count == 1:
            place = places[0].name_for_date()
        else:
            place = u'Unknown location'
        return place

    _companies = None

    def _get_companies(self):
        if self._companies is None:
            self._companies = self.companies.all()
        return self._companies

    def get_companies_display(self, html=True):
        companies = self._get_companies()
        num = len(companies)
        if html:
            companies = ['<span itemscope itemtype="http://schema.org/TheaterGroup"><a itemprop="url" href="%s">%s</a></span>' % (x.get_absolute_url(), prettify(x)) for x in companies]
        else:
            companies = [str(x) for x in companies]
        if num > 2:
            s = u', '.join(companies[:num-2]) + u', ' + u', and '.join(companies[num-2:])
        elif num == 2:
            s = u' and '.join(companies)
        elif num == 1:
            s = companies[0]
        else:
            s = u''
        return mark_safe(s)

    def title(self):
        return self.get_companies_display() or ''

    def creator(self):
        if self.source:
            return ''
        try:
            latest_version = Version.objects.get_for_object(self).order_by('revision__date_created')[0]
            return latest_version.revision.user
        except:
            return ''

    def last_modifier(self):
        try:
            latest_version = Version.objects.get_for_object(self).order_by('-revision__date_created')[0]
            return latest_version.revision.user
        except:
            return ''

    def source_type(self):
        if 'Birmingham Libraries' in self.source:
            return 'Birmingham Libraries'
        return 'Other'


class Production_Companies(models.Model):
    production = models.ForeignKey(Production, on_delete=models.CASCADE)
    productioncompany = models.ForeignKey(ProductionCompany, verbose_name='company', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'production-company many-to-many'

    def __str__(self):
        return "%s's bit in %s" % (self.productioncompany, self.production)


# class Performance(models.Model):
#    production = models.ForeignKey(Production, on_delete=models.CASCADE)
#    date = models.DateField()
#    time = models.TimeField(blank=True, null=True)
#    duration = models.IntegerField(blank=True, null=True)
#    place = models.ForeignKey(Place, on_delete=models.CASCADE)
#
#    def __str__(self):
#        return '%s %s performance of %s at %s' % (self.date, self.time, self.production, self.place)


class ProductionPlaceManager(models.Manager):
    def get_queryset(self):
        qs = super(ProductionPlaceManager, self).get_queryset()
        qs = qs.exclude(production__source__startswith='<a href="http://wo')
        return qs


class Place(models.Model):
    production = models.ForeignKey(Production, on_delete=models.CASCADE)
    place = models.ForeignKey(PlacePlace, related_name='productions_here', on_delete=models.CASCADE)
    start_date = ApproximateDateField(blank=True)
    press_date = models.DateField(blank=True, null=True)
    end_date = ApproximateDateField(blank=True)

    objects = ProductionPlaceManager()

    def __str__(self):
        return "The part of production %d at %s, %s" % (self.production.id, self.place, self.date_summary())

    def date_summary(self):
        return pretty_date_range(self.start_date, self.press_date, self.end_date)

    def name_for_date(self):
        a_date = self.start_date or self.press_date or self.end_date
        return self.place.name_for_date(a_date)


class PartManager(models.Manager):
    def search(self, search):
        return self.get_queryset().filter(role__icontains=search).extra(select={'best_date': 'IFNULL(productions_place.press_date, IF(productions_place.end_date!="", productions_place.end_date, productions_place.start_date))'}).order_by('-best_date', 'production__place__press_date')

    def get_queryset(self):
        qs = super(PartManager, self).get_queryset()
        qs = qs.exclude(production__source__startswith='<a href="http://wo')
        return qs


class Part(models.Model):
    production = models.ForeignKey(Production, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    role = models.CharField(
        u'R\u00f4le', max_length=200, blank=True, help_text=u'e.g. \u201cRomeo\u201d or \u201cDirector\u201d')
    cast = models.NullBooleanField(
        null=True, blank=True, verbose_name='Cast/Crew',
        help_text=u'Crew includes all non-cast, from director to musicians to producers')
    credited_as = models.CharField(
        max_length=100, blank=True,
        help_text=u'if they were credited differently to their name, or \u201cuncredited\u201d')
    order = models.IntegerField(blank=True, null=True)
    start_date = ApproximateDateField(blank=True)
    end_date = ApproximateDateField(blank=True)

    objects = PartManager()

    def role_or_unknown(self, lowercase=False):
        if self.role:
            return self.role
        if lowercase:
            return 'unknown'
        return 'Unknown'

    def __str__(self):
        return '%s, %s in %s' % (self.person, self.role_or_unknown(True), self.production)

    def cast_string(self):
        if self.cast == 1:
            return 'Cast'
        elif self.cast == 0:
            return 'Crew'
        else:
            return 'Unknown'

    def date_summary(self):
        return pretty_date_range(self.start_date, None, self.end_date)


class Visit(models.Model):
    production = models.ForeignKey(Production, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    recommend = models.BooleanField(default=False)
    date = ApproximateDateField(blank=True, default='')

    class Meta:
        unique_together = (('user', 'production'),)

    def __str__(self):
        out = '%s saw %s' % (self.user, self.production)
        if self.recommend:
            out += ', recommended'
        return out

    # Might as well just return the URL for the production for now
    def get_absolute_url(self):
        return self.production.get_absolute_url()
