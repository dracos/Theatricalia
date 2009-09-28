import re # , difflib
import urllib
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.utils import simplejson
from django.db.models import Q, get_model
from shortcuts import render
from people.models import Person
from places.models import Place
from plays.models import Play
from productions.models import Part, Production
from sounds.metaphone import dm
from sounds.jarowpy import jarow
#from levenshtein import damerau, qnum
from productions.objshow import productions_for, productions_list
from common.models import AlertLocal
from forms import SearchForm

distance = jarow
threshold = 0.8

def autocomplete_construct_search(field_name):
    """Use different lookup methods depending on the notation"""
    if field_name.startswith('^'):
        return "%s__istartswith" % field_name[1:]
    elif field_name.startswith('='):
        return "%s__iexact" % field_name[1:]
    elif field_name.startswith('@'):
        return "%s__search" % field_name[1:]
    else:
        return "%s__icontains" % field_name

def search_autocomplete(request):
    """Searches in the fields of the given related model and returns the 
       result as a simple string to be used by the jQuery Autocomplete plugin"""

    query = request.GET.get('q', None)

    app_label = request.GET.get('app_label', None)
    model_name = request.GET.get('model_name', None)
    search_fields = request.GET.get('search_fields', None)

    if not search_fields or not app_label or not model_name or not query:
        return HttpResponseNotFound()

    # For database order of articles
    m = re.match('^(A|An|The) (.*)$(?i)', query)
    if m:
        article, rest = m.groups()
        field_name = search_fields.split(',')[0]
        q = Q( **{ str('%s__iendswith' % field_name):' %s' % article, str('%s__istartswith' % field_name):rest } )
    else:
        q = None

    model = get_model(app_label, model_name)
    for field_name in search_fields.split(','):
        name = autocomplete_construct_search(field_name)
        if q:
            q = q | Q( **{str(name):query} )
        else:
            q = Q( **{str(name):query} )
    if search_fields == 'first_name,last_name' and ' ' in query:
        first, last = query.split(' ')
        q = q | Q(first_name__icontains=first, last_name__icontains=last)
    if app_label == 'places' and ',' in query:
        name, town = query.rsplit(',', 1)
        q = q | Q(name__icontains=name, town__icontains=town)

    qs = model.objects.filter( q )[:20]
    data = ''.join([u'%s|%s\n' % (f.__unicode__(), f.pk) for f in qs])
    return HttpResponse(data)

def search_people(search, force_similar=False, use_distance=True):
    people = []
    sounds_people = 0
    names = search.split(None, 3)
    if len(names)==1:
        names[0] = names[0].replace(u'\u2019', "'")
        if force_similar:
            people = Person.objects.exclude(first_name__icontains=names[0]).exclude(last_name__iexact=names[0])
        else:
            people = Person.objects.filter(Q(first_name__icontains=names[0]) | Q(last_name__iexact=names[0]))
        if force_similar:
            sounds_people = 2
            dm_, dm_alt = dm(names[0])
            people = people.filter(
                Q(first_name_metaphone=dm_) | Q(last_name_metaphone=dm_)
            )
        elif not people and re.match('[a-z\s\'-]+$(?i)', names[0]):
            sounds_people = 1
            dm_, dm_alt = dm(names[0])
            people = Person.objects.filter(
                Q(first_name_metaphone=dm_) | Q(last_name_metaphone=dm_)
                #Q(first_name_metaphone=dm_alt) | #Q(first_name_metaphone_alt=dm_) |
                #Q(last_name_metaphone_alt=dm_) | #Q(last_name_metaphone=dm_alt)
            )
        #if not people:
        #    allnames = []
        #    for p in Person.objects.all():
        #        allnames.extend((p.first_name, p.last_name))
        #    people = difflib.get_close_matches(names[0], allnames)
        #    people = Person.objects.filter(Q(first_name__in=people) | Q(last_name__in=people))
        if not people and use_distance:
            people = []
            for p in Person.objects.all():
                sim = distance(names[0].lower(), p.first_name.lower())
                sim2 = distance(names[0].lower(), p.last_name.lower())
                if sim >= threshold or sim2 >= threshold:
                    people.append((1-max(sim, sim2), p))
            people.sort()
            people = [ person for _, person in people ]
    elif len(names)==2:
        names[1] = names[1].replace(u'\u2019', "'")
        people = Person.objects.filter(first_name__icontains=names[0], last_name__iexact=names[1])
        if (not people and re.match('[a-z\s\'-]+$(?i)', search)) or force_similar:
            sounds_people = 1
            dm_first, dm_first_alt = dm(names[0])
            dm_last, dm_last_alt = dm(names[1])
            people = Person.objects.filter(
                # First name homophone, Last name match
                Q(first_name_metaphone=dm_first,     last_name__iexact=names[1]) |
                Q(first_name_metaphone=dm_first_alt, last_name__iexact=names[1]) |
                Q(first_name_metaphone_alt=dm_first, last_name__iexact=names[1]) |
                # First name match, last name homophone
                Q(first_name__icontains=names[0],    last_name_metaphone=dm_last) |
                Q(first_name__icontains=names[0],    last_name_metaphone_alt=dm_last) |
                Q(first_name__icontains=names[0],    last_name_metaphone=dm_last_alt) |
                # Both names homophones
                Q(first_name_metaphone=dm_first, last_name_metaphone=dm_last) |
                Q(first_name_metaphone=dm_first, last_name_metaphone_alt=dm_last) |
                Q(first_name_metaphone=dm_first, last_name_metaphone=dm_last_alt) |
                Q(first_name_metaphone=dm_first_alt, last_name_metaphone=dm_last) |
                Q(first_name_metaphone=dm_first_alt, last_name_metaphone_alt=dm_last) |
                Q(first_name_metaphone=dm_first_alt, last_name_metaphone=dm_last_alt) |
                Q(first_name_metaphone_alt=dm_first, last_name_metaphone=dm_last) |
                Q(first_name_metaphone_alt=dm_first, last_name_metaphone_alt=dm_last) |
                Q(first_name_metaphone_alt=dm_first, last_name_metaphone=dm_last_alt)
            )
        if not people and use_distance:
            people = []
            people2 = []
            people3 = []
            for p in Person.objects.all():
                sim = distance(names[0].lower(), p.first_name.lower())
                sim2 = distance(names[1].lower(), p.last_name.lower())
                simB = distance(' '.join(names).lower(), ('%s %s' % (p.first_name, p.last_name)).lower())
                if names[1].lower() == p.last_name.lower() and sim >= threshold:
                    people.append((1-sim, p))
                elif re.search(names[0], p.first_name, re.I) and sim2 >= threshold:
                    people2.append((1-sim2, p))
                elif simB >= threshold:
                    people3.append((1-simB, p))
                elif sim >= threshold and sim2 >= threshold:
                    people3.append((1-max(sim, sim2), p))
            people.sort()
            people2.sort()
            people3.sort()
            people = people + people2 + people3
            people = [ person for _, person in people ]
    elif len(names)==3:
        names[1] = names[1].replace(u'\u2019', "'")
        names[2] = names[2].replace(u'\u2019', "'")
        people = Person.objects.filter(
            Q(first_name__icontains=' '.join(names[0:2]), last_name__iexact=names[2]) |
            Q(first_name__icontains=names[0], last_name__iexact=' '.join(names[1:3]))
        )
    return people, sounds_people

def search_geonames(s):
    r = urllib.urlopen('http://ws.geonames.org/searchJSON?isNameRequired=true&style=LONG&q=' + urllib.quote(s.encode('utf-8')) + '&maxRows=20').read()
    r = simplejson.loads(r)
    return r

# For pagination of parts search
def search_parts(request, search):
    return productions_list(request, search, 'parts', 'search-parts.html')

# For pagination of search around
def search_around(request, search, type=''):
    search = search.strip()
    m = re.match('([-\d.]+)\s*,\s*([-\d.]+)$', search)

    if m:
        lat, lon = m.groups()
        name = request.GET.get('name', '')
    elif validate_postcode(search):
        loc = urllib.urlopen('http://ernestmarples.com/?p=%s&f=csv' % urllib.quote(search)).read()
        pc, lat, lon = loc.strip().split(',')
        name = re.sub('(\d[A-Z]{2})', r' \1', search.upper())
    elif validate_partial_postcode(search):
        r = urllib.urlopen('http://ws.geonames.org/postalCodeSearchJSON?country=gb&postalcode=' + urllib.quote(search)).read()
        r = simplejson.loads(r)
        lat, lon = r['postalCodes'][0]['lat'], r['postalCodes'][0]['lng']
        name = search.upper()
    else:
        raise Exception, 'Bad request'

    places = Place.objects.around(float(lat), float(lon))
    if not type:
        past, future = productions_for(places, 'places')
        alert = AlertLocal.objects.filter(user=request.user, latitude=lat, longitude=lon)
        return render(request, 'search-around.html', {
            'places': places,
            'past': past,
            'future': future,
            'lat': lat,
            'lon': lon,
            'latlon': '%s,%s' % (lat, lon),
            'name': name,
            'alert': alert,
        })
    return productions_list(request, places, type, 'search-around-productions.html', {
        'lat': lat,
        'lon': lon,
    })

def validate_postcode(postcode):
    end  = 'ABD-HJLNP-UW-Z';
    fst = 'A-PR-UWYZ';
    sec = 'A-HJ-Y';
    thd = 'A-HJKSTUW';
    fth = 'ABEHMNPRVWXY';

    if (re.match("(?i)[%s][1-9]\s*[0-9][%s][%s]$" % (fst, end, end), postcode) or
            re.match("(?i)[%s][1-9][0-9]\s*[0-9][%s][%s]$" % (fst, end, end), postcode) or
            re.match("(?i)[%s][%s][0-9]\s*[0-9][%s][%s]$" % (fst, sec, end, end), postcode) or
            re.match("(?i)[%s][%s][1-9][0-9]\s*[0-9][%s][%s]$" % (fst, sec, end, end), postcode) or
            re.match("(?i)[%s][1-9][%s]\s*[0-9][%s][%s]$" % (fst, thd, end, end), postcode) or
            re.match("(?i)[%s][%s][1-9][%s]\s*[0-9][%s][%s]$" % (fst, sec, fth, end, end), postcode)):
        return True
    else:
        return False

def validate_partial_postcode(postcode):
    fst = 'A-PR-UWYZ';
    sec = 'A-HJ-Y';
    thd = 'A-HJKSTUW';
    fth = 'ABEHMNPRVWXY';

    if (re.match("(?i)[%s][1-9]$" % (fst), postcode) or
            re.match("(?i)[%s][1-9][0-9]$" % (fst), postcode) or
            re.match("(?i)[%s][%s][0-9]$" % (fst, sec), postcode) or
            re.match("(?i)[%s][%s][1-9][0-9]$" % (fst, sec), postcode) or
            re.match("(?i)[%s][1-9][%s]$" % (fst, thd), postcode) or
            re.match("(?i)[%s][%s][1-9][%s]$" % (fst, sec, fth), postcode)):
        return True
    else:
        return False

def search(request):
    search = request.GET.get('q', '').strip()

    # Searching round a point, or a postcode
    m = re.match('([-\d.]+)\s*,\s*([-\d.]+)$', search)
    if m or validate_postcode(search) or validate_partial_postcode(search):
        return HttpResponseRedirect(reverse('search-around', args=[urllib.quote(search.encode('utf-8'))]))

    if search and len(search)<3:
        return render(request, 'search.html', {
            'error': 'Length',
            'search': search,
        })

    if search:
        m = re.match('^(A|An|The) (.*)$(?i)', search)
        if m:
            article, rest = m.groups()
            title_q = Q(title__iendswith=' %s' % article, title__istartswith=rest)
            name_q = Q(name__iendswith=' %s' % article, name__istartswith=rest)
        else:
            title_q = Q(title__icontains=search)
            name_q = Q(name__icontains=search)
        people, sounds_people = search_people(search, force_similar=request.GET.get('similar'), use_distance=False)
        near = search_geonames(search)
        places = Place.objects.filter(name_q | Q(town__icontains=search))
        plays = Play.objects.filter(title_q)
        parts = Paginator(Part.objects.search(search), 10, orphans=2).page(1)

        return render(request, 'search.html', {
            'people': people,
            'plays': plays,
            'places': places,
            'parts': parts,
            'near': near,
            'sounds_people': sounds_people,
            'search': search,
        })

    form = SearchForm(request.POST or None)
    return render(request, 'search-advanced.html', {
        'form': form,
    })
