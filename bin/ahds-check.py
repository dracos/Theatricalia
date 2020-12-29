#!/usr/bin/python
#
# Based on ahds-import.py
# This checks that the cast totals from AHDS match that in current/import revision in db
# outputting the ones that don't match (turns out all duplicates at the AHDS end)
# Checks Production.Place entries too

import re
import os
import sys
sys.path.append('../../')
sys.path.append('../')
os.environ['DJANGO_SETTINGS_MODULE'] = 'theatricalia.settings'

from productions.models import Part, Place
from reversion.models import Version


def fix_dots(s):
    return s.title().replace('.', ' ').replace('  ', ' ').strip()


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


for n in range(1, 67):
    file = open('../data/ahds/lists/%d' % n).read()
    m = re.search('<table width="90%" cellpadding="5" cellspacing="0" class="table01">(.*?)</table>(?s)', file)
    table = m.group(1)
    rows = re.findall('<tr[^>]*>(.*?)</tr>(?s)', table)
    for play_row in rows:
        play, author, director, designer, theatre, first, last = re.findall(r'<td[^>]*>\s*(.*?)\s*</td>(?s)', play_row)
        if play == '<b>Play</b>':
            continue
        if theatre in theatre_lookup:
            theatre = theatre_lookup[theatre]
        data = {
            'play': play,
            'theatre': theatre,
            'first': re.sub(r'^(\d\d)/(\d\d)/(\d+)$', r'19\3-\2-\1', re.sub(r'^(\d\d)/(\d)/(\d+)$', r'19\3-0\2-\1', re.sub(r'^(\d)/(\d\d)/(\d+)$', r'19\3-\2-0\1', re.sub(r'^(\d)/(\d)/(\d+)$', r'19\3-0\2-0\1', first)))),
            'last':  re.sub(r'^(\d\d)/(\d\d)/(\d+)$', r'19\3-\2-\1', re.sub(r'^(\d\d)/(\d)/(\d+)$', r'19\3-0\2-\1', re.sub(r'^(\d)/(\d\d)/(\d+)$', r'19\3-\2-0\1', re.sub(r'^(\d)/(\d)/(\d+)$', r'19\3-0\2-0\1', last)))),
        }
        if author:
            data['author'] = [fix_dots(x) for x in re.split(', ', author)]
        if director:
            data['director'] = [fix_dots(x) for x in re.split(', ', director)]
        if designer:
            data['designer'] = [fix_dots(x) for x in re.split(', ', designer)]
            if data['designer'][0] == 'Voytek':
                data['designer'].append('')

        m = re.match(r'<a href="birminghamrepdetails\.do\?id=(\d+)">(.*?)</a>$', data['play'])  # Always will match
        data['id'], data['play'] = m.groups()
        details = open('../data/ahds/details/%s' % data['id']).read()
        m = re.search('<table width="600px" cellpadding="3" cellspacing="0" class="table01">(.*?)</table>(?s)', details)
        table = m.group(1)
        detail_rows = re.findall(r"<tr class='(?:normal|alternate)Row01'>\s*<td class=\"column01\">(.*?)</td>\s*<td class=\"column02\">(.*?)</td>\s*</tr>(?s)", table)
        for row in detail_rows:
            key = re.sub(':$', '', row[0])
            value = re.sub('&#039;', "'", row[1].strip())
            value = re.sub('</?b>', '', value)
            if key == 'Cast':
                data['cast'] = [[fix_dots(y) for y in re.split(', ', x)] for x in re.split(r'\s*<br>\s*', value) if x]

        places = Place.objects.filter(production__source__endswith='=%s">AHDS record</a>)' % data['id'])
        if len(places) == 1 and places[0].place.name == data['theatre']:
            continue
        # if 'theatre' in data and data['theatre']:
            # location = add_theatre(data['theatre'])
            # ProductionPlace.objects.get_or_create(production=production, place=location, start_date=data['first'], end_date=data['last'])
        # else:
            # location, created = Place.objects.get_or_create(name='Unknown')
            # ProductionPlace.objects.get_or_create(production=production, place=location, start_date=data['first'], end_date=data['last'])
        print(places, data['theatre'])
        continue

        total = 0
        for c in data['cast']:
            if c[0] == 'Cast Unknown' or c[0] == "Playgoers' Society":
                continue
            total += 1

        if 'director' in data:
            total += 1

        if 'designer' in data:
            total += 1

        parts = Part.objects.filter(production__source__endswith='=%s">AHDS record</a>)' % data['id'])
        orig_parts = Version.objects.filter(revision=19230, object_id__in=parts).count()
        parts = parts.count()
        if orig_parts == total:
            continue
        print(data['id'], total, parts, orig_parts, data['play'])
