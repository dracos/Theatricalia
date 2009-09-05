#!/usr/bin/python

import os, sys, re

sys.path.append('../../')
sys.path.append('../')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings' 

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
        play, theatre, season, notes, search_link, details_link = re.findall('<td[^>]*>\s*(.*?)\s*</td>(?s)', row)
        # season is always n-(n+1)
        m = re.search('href="([^>]*?unique_key=(\d+)[^>]*?)">', search_link)
        search_link = m.group(1).replace('&amp;', '&').replace('\n', '').replace(' ', '%20')
        details_link = m.group(1).replace('&amp;', '&').replace('\n', '').replace(' ', '%20')
        id = m.group(2)
        print ' ', id, play, theatre, n, '-', (n+1)

        play, created = Play.objects.get_or_create(title=play)
        source = '<a href="http://www.bristol.ac.uk/theatrecollection/%s">University of Bristol Theatre Collection</a>' % search_link
        production = Production(
            play = play,
            description = notes,
            source = source,
        )
        production.save()

        location, created = Place.objects.get_or_create(name=theatre)
        start_date = '%d-00-00' % n
        end_date = '%d-00-00' % (n+1)
        ProductionPlace.objects.get_or_create(production=production, place=location, start_date=start_date, end_date=end_date)

        fp = open('../data/bristol/productions/%s' % id)
        details = fp.read()
        fp.close()
        if re.search('Unfortunately, we do not currently have any records for the performance you selected.', details):
            continue
        m = re.search('<table border="1" width="100%"[^>]*>(.*?)</table>(?s)', details)
        if not m:
            print id
        table = m.group(1)
        people_rows = re.findall('<tr[^>]*>(.*?)</tr>(?s)', table)
        for row in people_rows:
            if re.search('<th>', row): continue
            job, forename, surname = re.findall('<td[^>]*>\s*(.*?)\s*</td>', row)
            surname = surname.title()
            if job in 'Author':
                person, created = Person.objects.get_or_create(first_name=forename, last_name=surname)
                play.authors.add(person)
                continue
            elif job in ('Composer', 'Designer', 'Director'):
                cast = False
                role = job
            elif job == 'Actor':
                cast = True
                role = ''
            else:
                raise Exception
            person, created = Person.objects.get_or_create(first_name=forename, last_name=surname)
            part = Part.objects.get_or_create(production=production, person=person, role=role, cast=cast)

