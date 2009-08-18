#!/usr/bin/python

import os, sys, glob, re
from datetime import datetime

sys.path.append('../../')
sys.path.append('../')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings' 

from plays.models import Play
from productions.models import Production, Part, ProductionCompany
from productions.models import Place as ProductionPlace
from people.models import Person
from places.models import Place
from django.contrib.auth.models import User

def add_parts(str, cast):
    people = re.findall('<tr>\s*<td class="UnderviewKey">\s*&nbsp;</td>\s*<td class="UnderviewEntry"><p>(.*?)</p></td>\s*<td class="UnderviewEntry"><p>(.*?)</p></td>\s*<td class="AuthorityLink">', str)
    for person in people:
        name, role = person
        name = name.strip()
        role = role.strip()
        m = re.match('(.*?), (.*)$', name)
        if m:
            first_name, last_name = m.group(2), m.group(1)
            name = '%s %s' % (first_name, last_name)
        else:
            first_name, last_name = '', name
        if name=='Sion Tudor Owen':
            first_name, last_name = 'Sion', 'Tudor-Owen'
        if name=='Oliver Ford Davies':
            first_name, last_name = 'Oliver', 'Ford-Davies'
        if name=='Cedric Thorpe-Davie':
            first_name, last_name = 'Cedric Thorpe', 'Davie'
        if name=='John Lloyd-Fillingham':
            first_name, last_name = 'John Lloyd', 'Fillingham'
        if name == 'J Denton Thompson':
            first_name, last_name = 'J', 'Denton-Thompson'
        if name == 'David Shaw Parker':
            first_name, last_name = 'David', 'Shaw-Parker'
        if name == 'Dugald Bruce Lockhart':
            first_name, last_name = 'Dugald', 'Bruce-Lockhart'
        if name == 'Riette Sturge Moore' or name == 'Riette Sturge-Moore':
            first_name, last_name = 'Riette', 'Sturge Moore'

        person, created = Person.objects.get_or_create(first_name=first_name, last_name=last_name)
        part = Part.objects.get_or_create(production=production, person=person, role=role, cast=cast)

# Main

rsc, created = ProductionCompany.objects.get_or_create(name='Royal Shakespeare Company')

for file in glob.glob('../data/rsc/dataProds/*'):
    r = open(file).read()
    print file

    data = {}
    matches = re.findall('<tr>\s*<td class="FieldLabel">(.*?)</td>\s*<td class="[^"]*">(.*?)\s*</td>', r)
    for match in matches:
        data[match[0]] = match[1]

    if not data['Title']: raise Exception, 'Missing Title'
    if not data['PressNight']: raise Exception, 'Missing press date'
    if not data['Venue']: raise Exception, 'Missing venue'
    if not data['PerfCode']: raise Exception, 'Missing production code'

    title = data['Title'].replace('&amp;', '&')
    play, created = Play.objects.get_or_create(title=title)

    playwrights = re.findall('<td class="UnderviewEntry"><p>(.*?)</p></td>\s*<td class="UnderviewEntry"><p>Playwright</p></td>', r)
    for p in playwrights:
        name = p.strip()
        m = re.match('(.*?), (.*)$', name)
        if m:
            first_name = m.group(2)
            last_name = m.group(1)
            name = '%s %s' % (first_name, last_name)
        else:
            first_name = ''
            last_name = name
        person, created = Person.objects.get_or_create(first_name=first_name, last_name=last_name)
        play.authors.add(person)

    press_date = datetime.strptime(re.sub('\s*(\d\d)/(\d\d)/(\d\d\d\d)\s*', r'\3-\2-\1', data['PressNight']), '%Y-%m-%d')

    location = re.sub('\.$', '', data['Venue'].strip())
    location = re.sub('^(A|An|The) (.*)$', r'\2, \1', location)
    location, created = Place.objects.get_or_create(name=location)

    end_date = re.sub('\s*(\d\d)/(\d\d)/(\d\d\d\d)\s*', r'\3-\2-\1', data.get('LastPerformed', ''))
            
    description = data.get('PerformanceNote', '')
    if 'NoPerformances' in data:
        description += ' (%s performance%s)' % (data['NoPerformances'], data['NoPerformances'] != 1 and 's' or '')
    description = description.strip()

    production = Production(
        play = play,
        company = rsc,
        description = description,
    )
    production.save()
    ProductionPlace.objects.get_or_create(production=production, place=location, press_date=press_date, end_date=end_date)

    m = re.search('<table summary="" class="UnderviewTable">\s*<tr>\s*<td class="UnderviewHeader" colspan=4>Creative Roles</td>\s*</tr>(.*?)</table>(?s)', r)
    if m:
        add_parts(m.group(1), False)
        r = r.replace(m.group(1), '')

    m = re.search('<table summary="" class="UnderviewTable">\s*<tr>\s*<td class="UnderviewHeader" colspan=4>Performers</td>\s*</tr>(.*?)</table>(?s)', r)
    if m:
        add_parts(m.group(1), True)
        r = r.replace(m.group(1), '')

    add_parts(r, None)

