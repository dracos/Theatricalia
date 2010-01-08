#!/usr/bin/python

import os, sys, re

sys.path.append('../../')
sys.path.append('../')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings' 

from functions import add_theatre
from plays.models import Play
from productions.models import Production, Part
from productions.models import Place as ProductionPlace
from people.models import Person
from places.models import Place

for n in range(1700,2009):
    file = '../data/bristol/years/%s.html' % n
    if not os.path.exists(file):
        continue
    print n
    fp = open(file)
    list = fp.read()
    fp.close()

    m = re.search('<table border="1" width="100%"[^>]*>(.*?)</table>(?s)', list)
    table = m.group(1)
    rows = re.findall('<tr[^>]*>(.*?)</tr>(?s)', table)
    for row in rows:
        if re.search('<th>', row): continue
        title, theatre, season, notes, search_link, details_link = re.findall('<td[^>]*>\s*(.*?)\s*</td>(?s)', row)
        # season is always n-(n+1)
        m = re.search('href="([^>]*?unique_key=(\d+)[^>]*?)">', search_link)
        search_link = m.group(1).replace('&amp;', '&').replace('\n', '').replace(' ', '%20')
        details_link = m.group(1).replace('&amp;', '&').replace('\n', '').replace(' ', '%20')
        id = m.group(2)
        if not theatre: theatre = 'Unknown'

        print ' ', id, title, theatre, n, '-', (n+1)

        fp = open('../data/bristol/productions/%s' % id)
        details = fp.read()
        fp.close()
        author = None
        people = []
        if not re.search('Unfortunately, we do not currently have any records for the performance you selected.', details):
            m = re.search('<table border="1" width="100%"[^>]*>(.*?)</table>(?s)', details)
            if not m:
                print id
                raise Exception
            table = m.group(1)
            people_rows = re.findall('<tr[^>]*>(.*?)</tr>(?s)', table)
            for row in people_rows:
                if re.search('<th>', row): continue
                job, forename, surname = re.findall('<td[^>]*>\s*(.*?)\s*</td>', row)
                forename = forename.title()
                surname = surname.title()
                if job in 'Author':
                    author = [ forename, surname ]
                elif job in ('Composer', 'Designer', 'Director'):
                    people.append([ forename, surname, False, job ])
                elif job == 'Actor':
                    people.append([ forename, surname, True, '' ])
                else:
                    raise Exception

        title = re.sub('^(A|An|The) (.*)$', r'\2, \1', title)
        if author:
            forename, surname = author
            person, created = Person.objects.get_or_create(first_name=forename, last_name=surname)
            try:
                play = Play.objects.get(title=title, authors=person)
            except:
                try:
                    play = Play.objects.get(title=title, authors=None)
                    play.authors.add(person)
                except:
                    play = Play(title=title)
                    play.save()
                    play.authors.add(person)
        else:
            try:
                play = Play.objects.get(title=title, authors=None)
            except:
                play = Play(title=title)
                play.save()

        source = '<a href="http://www.bristol.ac.uk/theatrecollection/search/%s">University of Bristol Theatre Collection</a>' % search_link
        production = Production(
            play = play,
            description = notes,
            source = source,
        )
        production.save()

        location = add_theatre(theatre)
        start_date = '%d-00-00' % n
        end_date = '%d-00-00' % (n+1)
        ProductionPlace.objects.get_or_create(production=production, place=location, start_date=start_date, end_date=end_date)

        for forename, surname, cast, role in people:
            person, created = Person.objects.get_or_create(first_name=forename, last_name=surname)
            part = Part.objects.get_or_create(production=production, person=person, role=role, cast=cast)

