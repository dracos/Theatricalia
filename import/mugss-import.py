#!/usr/bin/python

import re, os, sys
from xml.dom import minidom
sys.path.append('../../')
sys.path.append('../')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from functions import add_theatre, add_photo
from plays.models import Play
from productions.models import Production, Part, Place as ProductionPlace, ProductionCompany
from people.models import Person
from places.models import Place

company, created = ProductionCompany.objects.get_or_create(name="Manchester Universities Gilbert and Sullivan Society")

for filename in sorted(os.listdir('../data/mugss')):
    print filename
    data = minidom.parse('../data/mugss/%s' % filename)
    title = data.getElementsByTagName('title')[0].firstChild.data
    title = re.sub('^(A|An|The) (.*)$', r'\2, \1', title)
    print title
    play = Play.objects.get(title=title)
