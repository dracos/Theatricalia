import re # , difflib
import urllib
from datetime import datetime
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseNotFound
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
from common.templatetags.prettify import prettify

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

    qs = model.objects.filter( q )
    data = ''.join([u'%s|%s\n' % (f.__unicode__(), f.pk) for f in qs])
    return HttpResponse(data)

def search_people(search, force_similar=False, use_distance=True):
    people = []
    sounds_people = 0
    names = search.split(None, 3)
    if len(names)==1:
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
        elif not people:
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
        people = Person.objects.filter(first_name__icontains=names[0], last_name__iexact=names[1])
        if not people or force_similar:
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
        people = Person.objects.filter(
            Q(first_name__icontains=' '.join(names[0:2]), last_name__iexact=names[2]) |
            Q(first_name__icontains=names[0], last_name__iexact=' '.join(names[1:3]))
        )
    return people, sounds_people

def search_geonames(s):
    r = urllib.urlopen('http://ws.geonames.org/searchJSON?isNameRequired=true&style=LONG&q=' + s + '&maxRows=20').read()
    r = simplejson.loads(r)
    return r

# For pagination of parts search
def search_parts(request, search):
    return productions_list(request, search, 'parts', 'search-parts.html')

# For pagination of search around
def search_around(request, latlon, type=''):
    m = re.match('\s*([-\d.]+)\s*,\s*([-\d.]+)\s*$', latlon)
    if not m:
        raise Exception, 'Bad request'

    lat, lon = m.groups()
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
            'name': request.GET.get('name', ''),
            'alert': alert,
        })
    return productions_list(request, places, type, 'search-around-productions.html', {
        'lat': lat,
        'lon': lon,
    })

def search(request):
    search = request.GET.get('q', '')
    people = plays = places = near = parts = []
    sounds_people = 0

    # Searching round a point
    m = re.match('\s*([-\d.]+)\s*,\s*([-\d.]+)\s*$', search)
    if m:
        return search_around(request, search)

    if search:
        people, sounds_people = search_people(search, force_similar=request.GET.get('similar'), use_distance=False)
        near = search_geonames(search)
        places = Place.objects.filter(Q(name__icontains=search) | Q(town__icontains=search))
        plays = Play.objects.filter(title__icontains=search)
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
