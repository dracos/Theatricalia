#!/usr/bin/python

import os, sys, glob, re
from datetime import datetime

sys.path.append('../../')
sys.path.append('../')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings' 

from productions.models import Production, Part
from people.models import Person
from utils import base32_to_int

def get_person(name):
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
    if last_name == 'Stoppard' or last_name == 'Smith' or last_name == 'Gielgud' or last_name=='Richardson':
        first_name = first_name.replace('Sir ', '').replace('Dame ', '')
    if last_name == 'Priestley' and first_name == 'John Boynton':
        first_name = 'J. B.'
    if last_name == 'Sophocles (c496-406/5 BC)':
        last_name = 'Sophocles'
    if last_name == 'Maugham':
        first_name = 'W. Somerset'
    if first_name == 'Sir James M' and last_name == 'Barrie':
        first_name = 'J. M.'
    if first_name == 'Ena Lamont' and last_name == 'Stewart':
        first_name = 'Ena'
        last_name = 'Lamont Stewart'

    multis = {
        ('Robert', 'Walker'): '3ga',
        ('John', 'David'): 'zcb',
        ('Mike', 'Ockrent'): '4y3',
        ('Lucy', 'Bailey'): '19pc',
        ('Geoffrey', 'Hutchings'): '3q7',
        ('Tom', 'Watson'): '8he',
        ('Oliver Ford', 'Davies'): '115k',
        ('David', 'Price'): '20c',
        ('Giles', 'Croft'): '11mx',
        ('Paul', 'Harris'): 'x6x',
        ('Mark', 'Smith'): '12dj',
        ('Anita', 'Dobson'): '13na',
        ('Tim', 'Mitchell'): '84g',
        ('Caroline', 'Smith'): '1jj8',
        ('Richard', 'Harvey'): '1jxd',
        ('Richard', 'Owen'): '1jyh',
        ('Jill', 'McMillan'): '1hbq',
        ('Anthony', 'Howell'): '8g1',
        ('Laura', 'Williams'): '1dmj',
        ('Mark', 'Pollard'): '18v6',
        ('Robert', 'Day'): '1hfe',
        ('Jeremy', 'Franklin'): '9wh',
        ('Jack', 'O\'Brien'): '1kcs',
        ('John', 'Adams'): '16y7',
        ('David', 'Graham'): 'vfy',
        ('Alan', 'Jackson'): '1hpd',
        ('James', 'Barry'): '18ww',
    }
    if (first_name, last_name) in multis:
        person = Person.objects.get(id=base32_to_int(multis[(first_name, last_name)]))
    else:
        try:
            person = Person.objects.get(first_name=first_name, last_name=last_name)
        except:
            person = None
            
    return person

wrong = 0

def fix_parts(str, cast):
    global wrong
    people = re.findall('<tr>\s*<td class="UnderviewKey">\s*&nbsp;</td>\s*<td class="UnderviewEntry">\s*(.*?)\s*</td>\s*<td class="UnderviewEntry">\s*(.*?)\s*</td>\s*<td class="AuthorityLink">', str)
    for person in people:
        name, role = person
        if not name and not role:
            continue
        person = get_person(name)
        if not person:
            continue
        try:
            part = Part.objects.get(production=production, person=person, role=role.decode('iso-8859-1'))
            part.cast = cast
            part.save()
        except Exception, e:
            wrong += 1
            #print wrong, person, e 

# Main

g = glob.glob('../data/national/productions/*')
g.sort()
for file in g:
    if re.search('19[678]', file):
        continue
    r = open(file).read()
    print file

    data = {}
    matches = re.findall('(?s)<tr>\s*<td class="FieldLabel">\s*(.*?)\s*</td>\s*<td class="[^"]*">\s*(.*?)\s*</td>', r)
    for match in matches:
        data[match[0]] = match[1]

    if not data['PerfCode']: raise Exception, 'Missing production code'
    m = re.search('dsqItem=(.*?)#HERE', data['PerfCode'])
    code = m.group(1)
    source = '<a href="http://worthing.nationaltheatre.org.uk/Dserve/dserve.exe?dsqIni=Dserve.ini&dsqApp=Archive&dsqCmd=show.tcl&dsqDb=Performance&dsqSearch=%28PerfCode=%27' + code + '%27%29">National Theatre Performance Database</a>'
    production = Production.objects.get( source = source )

    m = re.search('(?i)<table summary="" class="UnderviewTable">\s*<tr>\s*<td class="UnderviewHeader" colspan=4><p align="center"><font color="#990000" size="4">Creative Roles</font></p></td>\s*</tr>(.*?)</table>(?s)', r)
    if m:
        fix_parts(m.group(1), False)
        r = r.replace(m.group(1), '')

    m = re.search('(?i)<table summary="" class="UnderviewTable">\s*<tr>\s*<td class="UnderviewHeader" colspan=4><p align="center"><font color="#990000" size="4">Performers</font></p></td>\s*</tr>(.*?)</table>(?s)', r)
    if m:
        fix_parts(m.group(1), True)
        r = r.replace(m.group(1), '')

    fix_parts(r, None)

