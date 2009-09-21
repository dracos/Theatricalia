#!/usr/bin/python

import re, os, sys
sys.path.append('../../')
sys.path.append('../')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from plays.models import Play
from productions.models import Production, Part, Place as ProductionPlace, ProductionCompany
from people.models import Person
from places.models import Place
from django.contrib.auth.models import User

def fix_dots(s):
    return s.title().replace('.', ' ').replace('  ', ' ').strip()

def add_person_nicely(first_name, last_name):
    person, created = Person.objects.get_or_create(first_name=first_name, last_name=last_name)
    return person

# Manual list from some already existing Places
theatre_lookup = {
   "Comedy, London": "Comedy Theatre, London",
   "Duchess, London": "Duchess Theatre, London",
   "Globe, London": "Globe Theatre, London",
   "King's, Glasgow": "King's Theatre, Glasgow",
   "Kingsway, London": "Kingsway Theatre, London",
   "Lyceum, Edinburgh": "Lyceum Theatre, Edinburgh",
   "Lyric, London": "Lyric Theatre, London",
   "Malvern": "Malvern Theatre, Worcestershire",
   "New, London": "New Theatre, London",
   "Palace, Manchester": "Palace Theatre, Manchester",
   "Piccadilly, London": "Piccadilly Theatre, London",
   "Playhouse, London": "Playhouse Theatre, London",
   "Prince's, Manchester": "Prince's Theatre, Manchester",
   "Queen's, London": "Queen's Theatre, London",
   "Regent, London": "Regent Theatre, London",
   "Royalty, London": "The Royalty Theatre, London",
   "S. Bernhardt, Paris": "Sarah Bernhardt Theatre des Nations",
   "S.m.t., Stratford": "Shakespeare Memorial Theatre, Stratford-upon-Avon",
   "Vaudeville, London": "Vaudeville Theatre, London",
   "B'ham Rep": "Birmingham Repertory Theatre",
}

# Unique slugs not needed any more, but here's the code as was
#    try:
#        person = Person.objects.get(slug=slug)
#    except Person.DoesNotExist:
#        # Nothing with the slug exists at all, so go ahead and make one
#        person, created = Person.objects.get_or_create(first_name=first_name, last_name=last_name, slug=slug)
#    else:
#        # Something with the slug exists already
#        try:
#            person = Person.objects.get(first_name=first_name, last_name=last_name)
#        except Person.DoesNotExist:
#            # So we have same slug, but different names. Change the slug.
#            slug0 = slug
#            i = 2
#            while True:
#                slug = '%s-%s' % (slug0, i)
#                try:
#                    person = Person.objects.get(slug=slug)
#                except Person.DoesNotExist:
#                    break
#                else:
#                    i += 1
#            person, created = Person.objects.get_or_create(first_name=first_name, last_name=last_name, slug=slug)
#    return person

for n in range(1, 67):
    print n
    file = open('../data/ahds/lists/%d' % n).read()
    m = re.search('<table width="90%" cellpadding="5" cellspacing="0" class="table01">(.*?)</table>(?s)', file)
    table = m.group(1)
    rows = re.findall('<tr[^>]*>(.*?)</tr>(?s)', table)
    for play_row in rows:
        play, author, director, designer, theatre, first, last = re.findall('<td[^>]*>\s*(.*?)\s*</td>(?s)', play_row)
        if play == '<b>Play</b>':
            continue
        if theatre in theatre_lookup:
            theatre = theatre_lookup[theatre]
        data = {
            'play': play,
            'theatre': theatre,
            'first': re.sub('^(\d\d)/(\d\d)/(\d+)$', r'19\3-\2-\1', re.sub('^(\d\d)/(\d)/(\d+)$', r'19\3-0\2-\1', re.sub('^(\d)/(\d\d)/(\d+)$', r'19\3-\2-0\1', re.sub('^(\d)/(\d)/(\d+)$', r'19\3-0\2-0\1', first)))),
            'last':  re.sub('^(\d\d)/(\d\d)/(\d+)$', r'19\3-\2-\1', re.sub('^(\d\d)/(\d)/(\d+)$', r'19\3-0\2-\1', re.sub('^(\d)/(\d\d)/(\d+)$', r'19\3-\2-0\1', re.sub('^(\d)/(\d)/(\d+)$', r'19\3-0\2-0\1', last)))),
        }
        if author:
            data['author'] = [ fix_dots(x) for x in re.split(', ', author) ]
        if director:
            data['director'] = [ fix_dots(x) for x in re.split(', ', director) ]
        if designer:
            data['designer'] = [ fix_dots(x) for x in re.split(', ', designer) ]
            if data['designer'][0]=='Voytek':
                data['designer'].append('')

        m = re.match('<a href="birminghamrepdetails\.do\?id=(\d+)">(.*?)</a>$', data['play']) # Always will match
        data['id'], data['play'] = m.groups()
        details = open('../data/ahds/details/%s' % data['id']).read()
        m = re.search('<table width="600px" cellpadding="3" cellspacing="0" class="table01">(.*?)</table>(?s)', details)
        table = m.group(1)
        detail_rows = re.findall("<tr class='(?:normal|alternate)Row01'>\s*<td class=\"column01\">(.*?)</td>\s*<td class=\"column02\">(.*?)</td>\s*</tr>(?s)", table)
        for row in detail_rows:
            # All main details match from the index page, *checked*
            key = re.sub(':$', '', row[0])
            value = re.sub('&#039;', "'", row[1].strip())
            value = re.sub('</?b>', '', value)
            if key == 'Cast':
                data['cast'] = [ [ fix_dots(y) for y in re.split(', ', x)] for x in re.split('\s*<br>\s*', value) if x ]

        # Okay, got it all now. Let's stick it all in the db
        title = re.sub('^(A|An|The) (.*)$', r'\2, \1', data['play'])
        if 'author' in data:
            forename, surname = data['author'][1], data['author'][0]
            try:
                play = Play.objects.get(title__iexact=title, authors__last_name=surname, authors__first_name__startswith=forename[0])
            except:
                try:
                    play = Play.objects.get(title__istartswith="%s," % title, authors__last_name=surname, authors__first_name__startswith=forename[0])
                except:
                    person = add_person_nicely(forename, surname)
                    try:
                        play = Play.objects.get(title__iexact=title, authors=None)
                        play.authors.add(person)
                    except:
                        play = Play(title=title)
                        play.save()
                        play.authors.add(person)
        else:
            try:
                play = Play.objects.get(title__iexact=title, authors=None)
            except:
                play = Play(title=title)
                play.save()

        company = None
        for c in data['cast']:
            if c[0] == "Playgoers' Society":
                company, created = ProductionCompany.objects.get_or_create(name="Playgoers' Society")

        production = Production(play=play, company=company, source='AHDS Performing Arts (#' + data['id'] + ')')
        production.save()

        if 'theatre' in data and data['theatre']:
            theatre = re.sub('^(A|An|The) (.*)$', r'\2, \1', data['theatre'])
            theatre_no_the = re.sub(', (A|An|The)$', '', theatre)
            theatre_with_the = '%s, The' % theatre_no_the
            try:
                location = Place.objects.get(name=theatre_with_the)
            except:
                try:
                    location = Place.objects.get(name=theatre_no_the)
                except:
                    location, created = Place.objects.get_or_create(name=theatre)
            ProductionPlace.objects.get_or_create(production=production, place=location, start_date=data['first'], end_date=data['last'])
        else:
            location, created = Place.objects.get_or_create(name='Unknown')
            ProductionPlace.objects.get_or_create(production=production, place=location, start_date=data['first'], end_date=data['last'])

        for c in data['cast']:
            if c[0] == 'Cast Unknown' or c[0] == "Playgoers' Society":
                continue
            person = add_person_nicely(c[1], c[0])
            Part.objects.get_or_create(production=production, person=person, cast=True)

        if 'director' in data:
            director = add_person_nicely(data['director'][1], data['director'][0])
            part, created = Part.objects.get_or_create(production=production, person=director, cast=False, role="Director")

        if 'designer' in data:
            designer = add_person_nicely(data['designer'][1], data['designer'][0])
            part, created = Part.objects.get_or_create(production=production, person=designer, cast=False, role="Designer")

