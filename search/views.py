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
from productions.models import Part, Production, ProductionCompany, Place as ProductionPlace, Production_Companies
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

    query = query.strip()

    # Ignore author part of field for lookup
    if app_label == 'plays':
        query = re.sub(', by .*', '', query)

    q = None
    if app_label == 'places' and ',' in query:
        name, town = query.rsplit(',', 1)
        q = Q(name__icontains=name.strip(), town__icontains=town.strip())
        m = re.match('(A|An|The) (.*)$(?i)', name)
        if m:
            article, rest = m.groups()
            q = q | Q(name__iendswith=' %s' % article, name__istartswith=rest, town__icontains=town.strip())

    # For database order of articles
    m = re.match('(A|An|The) (.*)$(?i)', query)
    if m:
        article, rest = m.groups()
        field_name = search_fields.split(',')[0]
        qq = Q( **{ str('%s__iendswith' % field_name):' %s' % article, str('%s__istartswith' % field_name):rest } )
        if q:
            q = q | qq
        else:
            q = qq

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
            people = Person.objects.exclude(first_name__icontains=names[0]).exclude(last_name__icontains=names[0])
        else:
            people = Person.objects.filter(Q(first_name__icontains=names[0]) | Q(last_name__icontains=names[0]))
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
        people = Person.objects.filter(first_name__icontains=names[0], last_name__icontains=names[1])
        if (not people and re.match('[a-z\s\'-]+$(?i)', search)) or force_similar:
            sounds_people = 1
            dm_first, dm_first_alt = dm(names[0])
            dm_last, dm_last_alt = dm(names[1])
            qs = Q()
            if dm_first:
            #    # Both names homophones
                if dm_last:
                    qs |= Q(first_name_metaphone=dm_first, last_name_metaphone=dm_last) \
                        | Q(first_name_metaphone=dm_first, last_name_metaphone_alt=dm_last) \
                        | Q(first_name_metaphone_alt=dm_first, last_name_metaphone=dm_last) \
                        | Q(first_name_metaphone_alt=dm_first, last_name_metaphone_alt=dm_last)
                if dm_last_alt:
                    qs |= Q(first_name_metaphone=dm_first, last_name_metaphone=dm_last_alt) \
                        | Q(first_name_metaphone_alt=dm_first, last_name_metaphone=dm_last_alt)
                # First name homophone, Last name match
                qs |= Q(first_name_metaphone=dm_first,     last_name__icontains=names[1]) \
                    | Q(first_name_metaphone_alt=dm_first, last_name__icontains=names[1])
            if dm_first_alt:
                qs |= Q(first_name_metaphone=dm_first_alt, last_name__icontains=names[1])
                if dm_last:
                    qs |= Q(first_name_metaphone=dm_first_alt, last_name_metaphone=dm_last) \
                        | Q(first_name_metaphone=dm_first_alt, last_name_metaphone_alt=dm_last)
                if dm_last_alt:
                    qs |= Q(first_name_metaphone=dm_first_alt, last_name_metaphone=dm_last_alt)
            if dm_last:
                # First name match, last name homophone
                qs |= Q(first_name__icontains=names[0],    last_name_metaphone=dm_last) \
                    | Q(first_name__icontains=names[0],    last_name_metaphone_alt=dm_last)
            if dm_last_alt:
                qs |= Q(first_name__icontains=names[0],    last_name_metaphone=dm_last_alt)
            people = Person.objects.filter( qs )

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
            Q(first_name__icontains=' '.join(names[0:2]), last_name__icontains=names[2]) |
            Q(first_name__icontains=names[0], last_name__icontains=' '.join(names[1:3]))
        )
    elif len(names)==4:
        names[3] = names[3].replace(u'\u2019', "'")
        people = Person.objects.filter(
            Q(first_name__icontains=' '.join(names[0:3]), last_name__icontains=names[3]) |
            Q(first_name__icontains=names[0], last_name__icontains=' '.join(names[1:4]))
        )
    return people, sounds_people

def search_places(name_q, search):
    query = name_q
    query = query | Q(town__icontains=search)
    words = search.rsplit(None, 1)
    if len(words) == 2:
        query = query | Q(name__icontains=words[0], town__icontains=words[1])
    return Place.objects.filter(query)
  
def search_geonames(s):
    try:
        splurgle
        r = urllib.urlopen('http://ws.geonames.org/searchJSON?isNameRequired=true&style=LONG&q=' + urllib.quote(s.encode('utf-8')) + '&maxRows=20').read()
        r = simplejson.loads(r)
    except:
        r = ''
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
        r = urllib.urlopen('http://mapit.mysociety.org/postcode/%s' % urllib.quote(search)).read()
        loc = simplejson.loads(r)
        pc, lat, lon = loc['postcode'], loc['wgs84_lat'], loc['wgs84_lon']
        name = re.sub('(\d[A-Z]{2})', r' \1', search.upper())
    elif validate_partial_postcode(search):
        try:
            r = urllib.urlopen('http://mapit.mysociety.org/postcode/partial/' + urllib.quote(search)).read()
            r = simplejson.loads(r)
            lat, lon = r['wgs84_lat'], r['wgs84_lon']
        except:
            r, lat, lon = '', None, None
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
    fst_noO = 'A-NPR-UWYZ';
    sec = 'A-HJ-Y';
    thd = 'A-HJKSTUW';
    fth = 'ABEHMNPRVWXY';

    if (re.match("(?i)[%s][1-9]\s*[0-9][%s][%s]$" % (fst_noO, end, end), postcode) or
            re.match("(?i)[%s][1-9][0-9]\s*[0-9][%s][%s]$" % (fst_noO, end, end), postcode) or
            re.match("(?i)[%s][%s][0-9]\s*[0-9][%s][%s]$" % (fst, sec, end, end), postcode) or
            re.match("(?i)[%s][%s][1-9][0-9]\s*[0-9][%s][%s]$" % (fst, sec, end, end), postcode) or
            re.match("(?i)[%s][1-9][%s]\s*[0-9][%s][%s]$" % (fst_noO, thd, end, end), postcode) or
            re.match("(?i)[%s][%s][1-9][%s]\s*[0-9][%s][%s]$" % (fst, sec, fth, end, end), postcode)):
        return True
    else:
        return False

def validate_partial_postcode(postcode):
    fst = 'A-PR-UWYZ';
    fst_noO = 'A-NPR-UWYZ';
    sec = 'A-HJ-Y';
    thd = 'A-HJKSTUW';
    fth = 'ABEHMNPRVWXY';

    if (re.match("(?i)[%s][1-9]$" % (fst_noO), postcode) or
            re.match("(?i)[%s][1-9][0-9]$" % (fst_noO), postcode) or
            re.match("(?i)[%s][%s][0-9]$" % (fst, sec), postcode) or
            re.match("(?i)[%s][%s][1-9][0-9]$" % (fst, sec), postcode) or
            re.match("(?i)[%s][1-9][%s]$" % (fst_noO, thd), postcode) or
            re.match("(?i)[%s][%s][1-9][%s]$" % (fst, sec, fth), postcode)):
        return True
    else:
        return False

def search(request):
    person = request.GET.get('person', '').strip()
    place = request.GET.get('place', '').strip()
    play = request.GET.get('play', '').strip()
    if person and place:
        places = search_places(Q(name__icontains=place), place)
        places = list(places)
        people, sounds_people = search_people(person, False, False)
        people = list(people)
        productions = list(Production.objects.filter(parts__in=people, places__in=places).select_related('play'))
        parts = Part.objects.filter(production__in=productions, person__in=people).select_related('person')

        companiesM2M = Production_Companies.objects.filter(production__in=productions).select_related('productioncompany')
        m2m = {}
        for c in companiesM2M:
            m2m.setdefault(c.production_id, []).append( c.productioncompany )
        for p in productions:
            p._companies = m2m.get(p.id, [])

        placeM2M = ProductionPlace.objects.filter(production__in=productions).order_by('start_date', 'press_date', 'end_date')
        venues = placeM2M.filter(place__in=places).select_related('place')
        m2m = {}
        for p in placeM2M:
            m2m.setdefault(p.production_id, []).append( p )
        for p in productions:
            p._place_set = m2m.get(p.id, [])

        m2m = {}
        for p in venues:
            m2m.setdefault(p.production_id, []).append( p.place )
        for p in productions:
            p.searched_places = m2m.get(p.id, [])
        m2m = {}
        for p in parts:
            m2m.setdefault(p.production_id, []).append( p.person )
        for p in productions:
            p.searched_people = m2m.get(p.id, [])

        return render(request, 'places/productions.html', {
            'productions': productions,
            'places': places,
            'people': people,
        })
    if person and play:
        title_q = Q(title__icontains=play)
        m = re.match('^(A|An|The) (.*)$(?i)', play)
        if m:
            article, rest = m.groups()
            title_q = title_q | Q(title__iendswith=' %s' % article, title__istartswith=rest)
        plays = Play.objects.filter(title_q)
        plays = list(plays)
        people, sounds_people = search_people(person, False, False)
        people = list(people)
        productions = list(Production.objects.filter(parts__in=people, play__in=plays).select_related('play'))

        return render(request, 'places/productions.html', {
            'productions': productions,
            'plays': plays,
            'people': people,
        })

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
        title_q = Q(title__icontains=search)
        name_q = Q(name__icontains=search)
        m = re.match('^(A|An|The) (.*)$(?i)', search)
        if m:
            article, rest = m.groups()
            title_q = title_q | Q(title__iendswith=' %s' % article, title__istartswith=rest)
            name_q = name_q | Q(name__iendswith=' %s' % article, name__istartswith=rest)
        people, sounds_people = search_people(search, force_similar=request.GET.get('similar'), use_distance=False)
        near = search_geonames(search)
        places = search_places(name_q, search)
        companies = ProductionCompany.objects.filter(name_q | Q(description__icontains=search))
        plays = Play.objects.filter(title_q)
        parts = Paginator(Part.objects.search(search), 10, orphans=2)

        try:
            near_length = len(near.geonames)
        except:
            near_length = 0
        if parts.count + companies.count() + plays.count() + places.count() + people.count() + near_length == 1:
            if companies.count():
                return HttpResponseRedirect(companies[0].get_absolute_url())
            if plays.count():
                return HttpResponseRedirect(plays[0].get_absolute_url())
            if places.count():
                return HttpResponseRedirect(places[0].get_absolute_url())
            if people.count():
                return HttpResponseRedirect(people[0].get_absolute_url())
            if near_length:
                place = near.geonames[0]
                return HttpResponseRedirect('/search/around/%s,%s?name=%s' % (place.lat, place.lng, place.name) )
            if parts.count:
                return HttpResponseRedirect(parts.page(1).object_list[0].production.get_absolute_url())

        parts = parts.page(1)

        return render(request, 'search.html', {
            'people': people,
            'plays': plays,
            'places': places,
            'companies': companies,
            'parts': parts,
            'near': near,
            'sounds_people': sounds_people,
            'search': search,
        })

    form = SearchForm(request.POST or None)
    return render(request, 'search-advanced.html', {
        'form': form,
    })
