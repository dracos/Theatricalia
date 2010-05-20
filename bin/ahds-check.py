#!/usr/bin/python
#
# Lots of code copied from ahds-import.py
# This checks that the cast totals from AHDS match that in current/import revision in db
# outputting the ones that don't match (all duplicates at the AHDS end)

import re, os, sys
sys.path.append('../../')
sys.path.append('../')
os.environ['DJANGO_SETTINGS_MODULE'] = 'theatricalia.settings'

from productions.models import Part
from reversion.models import Version

def fix_dots(s):
    return s.title().replace('.', ' ').replace('  ', ' ').strip()

for n in range(1, 67):
    file = open('../data/ahds/lists/%d' % n).read()
    m = re.search('<table width="90%" cellpadding="5" cellspacing="0" class="table01">(.*?)</table>(?s)', file)
    table = m.group(1)
    rows = re.findall('<tr[^>]*>(.*?)</tr>(?s)', table)
    for play_row in rows:
        play, author, director, designer, theatre, first, last = re.findall('<td[^>]*>\s*(.*?)\s*</td>(?s)', play_row)
        if play == '<b>Play</b>':
            continue
        data = {}
        if director:
            data['director'] = [ fix_dots(x) for x in re.split(', ', director) ]
        if designer:
            data['designer'] = [ fix_dots(x) for x in re.split(', ', designer) ]
            if data['designer'][0]=='Voytek':
                data['designer'].append('')

        m = re.match('<a href="birminghamrepdetails\.do\?id=(\d+)">(.*?)</a>$', play) # Always will match
        data['id'], play = m.groups()
        details = open('../data/ahds/details/%s' % data['id']).read()
        m = re.search('<table width="600px" cellpadding="3" cellspacing="0" class="table01">(.*?)</table>(?s)', details)
        table = m.group(1)
        detail_rows = re.findall("<tr class='(?:normal|alternate)Row01'>\s*<td class=\"column01\">(.*?)</td>\s*<td class=\"column02\">(.*?)</td>\s*</tr>(?s)", table)
        for row in detail_rows:
            key = re.sub(':$', '', row[0])
            value = re.sub('&#039;', "'", row[1].strip())
            value = re.sub('</?b>', '', value)
            if key == 'Cast':
                data['cast'] = [ [ fix_dots(y) for y in re.split(', ', x)] for x in re.split('\s*<br>\s*', value) if x ]

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
        print data['id'], total, parts, orig_parts, play

