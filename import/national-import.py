#!/usr/bin/python

import os, sys, glob, re
from datetime import datetime

sys.path.append('../../')
sys.path.append('../')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings' 

from fields import ApproximateDate
from plays.models import Play
from productions.models import Production, Part
from productions.models import Place as ProductionPlace
from people.models import Person
from places.models import Place

def get_name(name):
    m = re.match('(.*?); (.*)$', name)
    if m:
        first_name, last_name = m.group(2), m.group(1)
        name = '%s %s' % (first_name, last_name)
    else:
        first_name, last_name = '', name
    year = None
    m = re.match('(.*) \((\d+)\s*-', first_name)
    if m:
        first_name, year = m.groups()
    m = re.match('(.*) \(\s*-', first_name)
    if m:
        first_name = m.group(1)
    first_name = re.sub('(Sir|Lord|Dame);', r'\1', first_name)
    first_name = first_name.decode('iso-8859-1')
    last_name = last_name.decode('iso-8859-1')
    return first_name, last_name, year

def add_parts(str, cast):
    people = re.findall('<tr>\s*<td class="UnderviewKey">\s*&nbsp;</td>\s*<td class="UnderviewEntry">\s*(.*?)\s*</td>\s*<td class="UnderviewEntry">\s*(.*?)\s*</td>\s*<td class="AuthorityLink">', str)
    for person in people:
        name, role = person
        if not name and not role:
            continue
        first_name, last_name, dob_year = get_name(name)
        person, created = Person.objects.get_or_create(first_name=first_name, last_name=last_name)
        if dob_year:
            person.dob = ApproximateDate(int(dob_year))
            person.save()
        part = Part.objects.get_or_create(production=production, person=person, role=role.decode('iso-8859-1'), cast=cast)

# Main

for file in glob.glob('../data/national/productions/*'):
    r = open(file).read()
    print file

    data = {}
    matches = re.findall('(?s)<tr>\s*<td class="FieldLabel">\s*(.*?)\s*</td>\s*<td class="[^"]*">\s*(.*?)\s*</td>', r)
    for match in matches:
        data[match[0]] = match[1]

    if not data['Title']: raise Exception, 'Missing Title'
    if not data['PerfCode']: raise Exception, 'Missing production code'

    title = data['Title'].decode('iso-8859-1').replace('&amp;', '&')
    title = re.sub('^(A|An|The) (.*)$', r'\2, \1', title)

    playwrights = re.findall('<td class="UnderviewEntry">\s*(.*?)\s*</td>\s*<td class="UnderviewEntry">Writer</td>', r)
    authors = []
    for p in playwrights:
        first_name, last_name, dob_year = get_name(p)
        person, created = Person.objects.get_or_create(first_name=first_name, last_name=last_name)
        if dob_year:
            person.dob = ApproximateDate(int(dob_year))
            person.save()
        authors.append(person)

    if len(authors)>1:
        play = Play(title=title)
        play.save()
        for author in authors:
            play.authors.add(author)
    elif len(authors)==1:
        person = authors[0]
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

    location = re.sub('\.$', '', data.get('Venue', ''))
    location = re.sub('^(A|An|The) (.*)$', r'\2, \1', location)
    location, created = Place.objects.get_or_create(name=location)

    start_date = re.sub('(\d+)/(\d+)/(\d\d\d\d)', r'\3-\1-\2', data.get('OpeningNight', ''))
    press_date = re.sub('(\d+)/(\d+)/(\d\d\d\d)', r'\3-\1-\2', data.get('PressNight', ''))
    press_date = press_date and datetime.strptime(press_date, '%Y-%m-%d') or None
    end_date   = re.sub('(\d+)/(\d+)/(\d\d\d\d)', r'\3-\1-\2', data.get('LastPerformed', ''))
            
    source = '<a href="http://worthing.nationaltheatre.org.uk/Dserve/dserve.exe?dsqIni=Dserve.ini&dsqApp=Archive&dsqCmd=show.tcl&dsqDb=Performance&dsqSearch=PerfCode==%27' + data['PerfCode'] + '%27">RSC Performance Database</a>'

    production = Production(
        play = play,
        source = source,
    )
    production.save()
    ProductionPlace.objects.get_or_create(production=production, place=location, start_date=start_date, press_date=press_date, end_date=end_date)

    m = re.search('<table summary="" class="UnderviewTable">\s*<tr>\s*<td class="UnderviewHeader" colspan=4><p align="center"><font color="#990000" size="4">Creative Roles</font></p></td>\s*</tr>(.*?)</table>(?s)', r)
    if m:
        add_parts(m.group(1), False)
        r = r.replace(m.group(1), '')

    m = re.search('<table summary="" class="UnderviewTable">\s*<tr>\s*<td class="UnderviewHeader" colspan=4><p align="center"><font color="#990000" size="4">Performers</font></p></td>\s*</tr>(.*?)</table>(?s)', r)
    if m:
        add_parts(m.group(1), True)
        r = r.replace(m.group(1), '')

    add_parts(r, None)

