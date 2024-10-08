import json
import re
# import difflib
import urllib.request
import urllib.parse
from django.apps import apps
from django.urls import reverse
from django.core.paginator import Paginator
from django.core.exceptions import FieldError
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, Http404
from django.db.models import Q
from django.shortcuts import render
from people.models import Person
from places.models import Place, Name
from plays.models import Play
from productions.models import Part, Production, ProductionCompany
from sounds.metaphone import dm
from sounds.jarowpy import jarow
# from levenshtein import damerau, qnum
from productions.objshow import productions_for, productions_list
from common.models import AlertLocal
from common.templatetags.prettify import prettify_list
from .forms import SearchForm

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
    try:
        limit = int(request.GET.get('limit', 100))
    except ValueError:
        limit = 100

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
        parent = town.strip()
        q = Q(name__icontains=name.strip(), town__icontains=town.strip())
        q = q | Q(name__icontains=name.strip(), parent__name__icontains=parent)
        m = re.match('(?i)(A|An|The) (.*)$', name)
        if m:
            article, rest = m.groups()
            q = q | Q(name__iendswith=' %s' % article, name__istartswith=rest, town__icontains=town.strip())
            q = q | Q(name__iendswith=' %s' % article, name__istartswith=rest, parent__name__icontains=parent)

    # For database order of articles
    m = re.match('(?i)(A|An|The) (.*)$', query)
    if m:
        article, rest = m.groups()
        field_name = search_fields.split(',')[0]
        qq = Q(**{str('%s__iendswith' % field_name): ' %s' % article, str('%s__istartswith' % field_name): rest})
        if q:
            q = q | qq
        else:
            q = qq

    if app_label == 'people' and model_name == 'person':
        people, dummy = search_people(query, False, False)
        qs = people[:limit]
    else:
        try:
            model = apps.get_model(app_label=app_label, model_name=model_name)
        except LookupError:
            raise Http404
        for field_name in search_fields.split(','):
            name = autocomplete_construct_search(field_name)
            if q:
                q = q | Q(**{str(name): query})
            else:
                q = Q(**{str(name): query})
        if search_fields == 'first_name,last_name' and ' ' in query:
            first, last = query.split(' ')
            q = q | Q(first_name__icontains=first, last_name__icontains=last)

        try:
            qs = model.objects.filter(q)[:limit]
        except FieldError:
            raise Http404

    results = [(f.__str__(), f.pk) for f in qs]

    if app_label == 'places':
        query_without_brackets = re.sub(r' \(.*?\)$', '', query)
        q = Q(name__icontains=query) | Q(name__icontains=query_without_brackets)
        qs = Name.objects.filter(q)[:limit]
        results = [(f.__str__(), f.place.pk) for f in qs] + results
        results = sorted(results, key=lambda f: f[0])

    data = ''.join(['%s|%s\n' % (f[0], f[1]) for f in results])
    return HttpResponse(data)


def search_people(search, force_similar=False, use_distance=True):
    people = []
    sounds_people = 0
    names = search.split(None, 3)
    if len(names) == 1:
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
        elif not people and re.match(r'(?i)[a-z\s\'-]+$', names[0]):
            sounds_people = 1
            dm_, dm_alt = dm(names[0])
            people = Person.objects.filter(
                Q(first_name_metaphone=dm_) | Q(last_name_metaphone=dm_)
                # Q(first_name_metaphone=dm_alt) | #Q(first_name_metaphone_alt=dm_) |
                # Q(last_name_metaphone_alt=dm_) | #Q(last_name_metaphone=dm_alt)
            )
        # if not people:
        #     allnames = []
        #     for p in Person.objects.all():
        #         allnames.extend((p.first_name, p.last_name))
        #     people = difflib.get_close_matches(names[0], allnames)
        #     people = Person.objects.filter(Q(first_name__in=people) | Q(last_name__in=people))
        if not people and use_distance:
            people = []
            for p in Person.objects.all():
                sim = distance(names[0].lower(), p.first_name.lower())
                sim2 = distance(names[0].lower(), p.last_name.lower())
                if sim >= threshold or sim2 >= threshold:
                    people.append((1-max(sim, sim2), p))
            people.sort()
            people = [person for _, person in people]
    elif len(names) == 2:
        names[1] = names[1].replace(u'\u2019', "'")
        people = Person.objects.filter(first_name__icontains=names[0], last_name__icontains=names[1])
        if (not people and re.match(r'(?i)[a-z\s\'-]+$', search)) or force_similar:
            sounds_people = 1
            dm_first, dm_first_alt = dm(names[0])
            dm_last, dm_last_alt = dm(names[1])
            qs = Q()
            if dm_first:
                # Both names homophones
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
            people = Person.objects.filter(qs)

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
            people = [person for _, person in people]
    elif len(names) == 3:
        names[1] = names[1].replace(u'\u2019', "'")
        names[2] = names[2].replace(u'\u2019', "'")
        people = Person.objects.filter(
            Q(first_name__icontains=' '.join(names[0:2]), last_name__icontains=names[2]) |
            Q(first_name__icontains=names[0], last_name__icontains=' '.join(names[1:3]))
        )
    elif len(names) == 4:
        names[3] = names[3].replace(u'\u2019', "'")
        people = Person.objects.filter(
            Q(first_name__icontains=' '.join(names[0:3]), last_name__icontains=names[3]) |
            Q(first_name__icontains=names[0], last_name__icontains=' '.join(names[1:4]))
        )
    return people, sounds_people


def search_places(name_q, search):
    query = name_q
    query = query | Q(town__icontains=search) | Q(parent__name__icontains=search)
    words = search.rsplit(None, 1)
    if len(words) == 2:
        query = query | Q(name__icontains=words[0], town__icontains=words[1])
    return Place.objects.filter(query)


def search_other_place_names(search):
    query = Q(name__icontains=search)
    words = search.rsplit(None, 1)
    if len(words) == 2:
        query = query | Q(name__icontains=words[0], place__town__icontains=words[1])
    out = []
    for n in Name.objects.filter(query):
        p = n.place
        p.other_name = str(n)
        out.append(p)
    return out


# For pagination of parts search
def search_parts(request, search):
    return productions_list(request, search, 'parts', 'search-parts.html')


# For pagination of search around
def search_around(request, s, type=''):
    s = s.strip()
    m = re.match(r'([-\d.]+)\s*,\s*([-\d.]+)$', s)

    if m:
        lat, lon = m.groups()
        name = request.GET.get('name', '')
    elif validate_postcode(s):
        try:
            r = urllib.request.urlopen('https://mapit.mysociety.org/postcode/%s' % urllib.parse.quote(s)).read()
            loc = json.loads(r)
            lat, lon = loc['wgs84_lat'], loc['wgs84_lon']
            name = re.sub(r'(\d[A-Z]{2})', r' \1', s.upper())
        except:
            return search(request, redirect_okay=False)
    elif validate_partial_postcode(s):
        try:
            r = urllib.request.urlopen('https://mapit.mysociety.org/postcode/partial/' + urllib.parse.quote(s)).read()
            r = json.loads(r)
            lat, lon = r['wgs84_lat'], r['wgs84_lon']
        except:
            return search(request, redirect_okay=False)
        name = s.upper()
    else:
        raise Http404()

    if not lat or not lon:
        return

    places = Place.objects.around(float(lat), float(lon))
    if not type:
        past, future = productions_for(places, 'places')
        alert = AlertLocal.objects.filter(user=request.user.id, latitude=lat, longitude=lon)
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
    end = 'ABD-HJLNP-UW-Z'
    fst = 'A-PR-UWYZ'
    fst_noO = 'A-NPR-UWYZ'
    sec = 'A-HJ-Y'
    thd = 'A-HJKSTUW'
    fth = 'ABEHMNPRVWXY'

    if (re.match(r"(?i)[%s][1-9]\s*[0-9][%s][%s]$" % (fst_noO, end, end), postcode) or
            re.match(r"(?i)[%s][1-9][0-9]\s*[0-9][%s][%s]$" % (fst_noO, end, end), postcode) or
            re.match(r"(?i)[%s][%s][0-9]\s*[0-9][%s][%s]$" % (fst, sec, end, end), postcode) or
            re.match(r"(?i)[%s][%s][1-9][0-9]\s*[0-9][%s][%s]$" % (fst, sec, end, end), postcode) or
            re.match(r"(?i)[%s][1-9][%s]\s*[0-9][%s][%s]$" % (fst_noO, thd, end, end), postcode) or
            re.match(r"(?i)[%s][%s][1-9][%s]\s*[0-9][%s][%s]$" % (fst, sec, fth, end, end), postcode)):
        return True
    else:
        return False


def validate_partial_postcode(postcode):
    fst = 'A-PR-UWYZ'
    fst_noO = 'A-NPR-UWYZ'
    sec = 'A-HJ-Y'
    thd = 'A-HJKSTUW'
    fth = 'ABEHMNPRVWXY'

    if (re.match("(?i)[%s][1-9]$" % (fst_noO), postcode) or
            re.match("(?i)[%s][1-9][0-9]$" % (fst_noO), postcode) or
            re.match("(?i)[%s][%s][0-9]$" % (fst, sec), postcode) or
            re.match("(?i)[%s][%s][1-9][0-9]$" % (fst, sec), postcode) or
            re.match("(?i)[%s][1-9][%s]$" % (fst_noO, thd), postcode) or
            re.match("(?i)[%s][%s][1-9][%s]$" % (fst, sec, fth), postcode)):
        return True
    else:
        return False


def search_advanced(request, person, place, play):
    people = []
    places = []
    plays = []
    count = 0

    productions = Production.objects.all()

    if person:
        people, sounds_people = search_people(person, False, False)
        people = list(people)
        productions = productions.filter(parts__in=people)
        count += 1

    if place:
        places = search_places(Q(name__icontains=place), place)
        places = list(places)
        productions = productions.filter(places__in=places)
        count += 1

    if play:
        title_q = Q(title__icontains=play)
        m = re.match('(?i)^(A|An|The) (.*)$', play)
        if m:
            article, rest = m.groups()
            title_q = title_q | Q(title__iendswith=' %s' % article, title__istartswith=rest)
        plays = Play.objects.filter(title_q)
        plays = list(plays)
        productions = productions.filter(play__in=plays)
        count += 1

    if count > 1:
        productions = list(productions.select_related('play'))
        Production.objects.prefetch_companies(productions)
        Production.objects.prefetch_places(productions)
        # placeM2M = Production.objects.prefetch_places(productions)

        if person:
            parts = Part.objects.filter(production__in=productions, person__in=people).select_related('person')
            m2m = {}
            for p in parts:
                m2m.setdefault(p.production_id, {}).setdefault(p.person, []).append(p.role_or_unknown(True))
            for p in productions:
                searched_people = m2m.get(p.id, {})
                searched_people = ['%s, %s' % (pers, prettify_list(roles)) for pers, roles in searched_people.items()]
                p.searched_people = searched_people
        # if place:
        #     venues = placeM2M.filter(place__in=places).select_related('place')
        #     m2m = {}
        #     for p in venues:
        #         m2m.setdefault(p.production_id, []).append( p.place )
        #     for p in productions:
        #         p.searched_places = m2m.get(p.id, [])

        form = SearchForm(request.GET or None)
        return render(request, 'search/productions.html', {
            'form': form,
            'productions': productions,
            'plays': plays,
            'places': places,
            'people': people,
        })

    if len(people) + len(places) + len(plays) == 1:
        if len(plays) == 1:
            return HttpResponseRedirect(plays[0].get_absolute_url())
        if len(places) == 1:
            return HttpResponseRedirect(places[0].get_absolute_url())
        if len(people) == 1:
            return HttpResponseRedirect(people[0].get_absolute_url())

    return render(request, 'search.html', {
        'people': people,
        'plays': plays,
        'places': places,
    })


def search(request, redirect_okay=True):
    person = request.GET.get('person', '').strip()
    place = request.GET.get('place', '').strip()
    play = request.GET.get('play', '').strip()
    if person or place or play:
        # Advanced search form
        return search_advanced(request, person, place, play)

    # Generic "search everything" box
    search = request.GET.get('q', '').strip()

    # Check if we're searching round a point, or a postcode, redirect if so
    m = re.match(r'([-\d.]+)\s*,\s*([-\d.]+)$', search)
    if search.lower() != 'dv8' and redirect_okay and (m or validate_postcode(search) or validate_partial_postcode(search)):
        return HttpResponseRedirect(reverse('search-around', args=[search]))

    if search and len(search) < 3:
        return render(request, 'search.html', {
            'error': 'Length',
            'search': search,
        })

    if search:
        title_q = Q(title__icontains=search)
        name_q = Q(name__icontains=search)
        m = re.match('(?i)^(A|An|The) (.*)$', search)
        if m:
            article, rest = m.groups()
            title_q = title_q | Q(title__iendswith=' %s' % article, title__istartswith=rest)
            name_q = name_q | Q(name__iendswith=' %s' % article, name__istartswith=rest)
        people, sounds_people = search_people(search, force_similar=request.GET.get('similar'), use_distance=False)
        places = search_places(name_q, search)
        other_place_names = search_other_place_names(search)
        companies = ProductionCompany.objects.filter(name_q | Q(description__icontains=search))
        plays = Play.objects.filter(title_q)
        parts = Paginator(Part.objects.search(search), 20, orphans=4)

        if parts.count + companies.count() + plays.count() + places.count() + people.count() == 1:
            if companies.count():
                return HttpResponseRedirect(companies[0].get_absolute_url())
            if plays.count():
                return HttpResponseRedirect(plays[0].get_absolute_url())
            if places.count():
                return HttpResponseRedirect(places[0].get_absolute_url())
            if people.count():
                return HttpResponseRedirect(people[0].get_absolute_url())
            if parts.count:
                return HttpResponseRedirect(parts.page(1).object_list[0].production.get_absolute_url())

        parts = parts.page(1)

        return render(request, 'search.html', {
            'people': people,
            'plays': plays,
            'places': places,
            'other_place_names': other_place_names,
            'companies': companies,
            'parts': parts,
            'sounds_people': sounds_people,
            'search': search,
        })

    form = SearchForm(request.POST or None)
    return render(request, 'search-advanced.html', {
        'form': form,
    })
