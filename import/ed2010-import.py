#!/usr/bin/python

import re, os, sys
from datetime import datetime
import simplejson
sys.path.append('../../')
sys.path.append('../')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from functions import add_theatre, real_run
from plays.models import Play
from productions.models import Production, Part, Place as ProductionPlace, ProductionCompany
from people.models import Person
from places.models import Place
from countries.models import Country

real_run()

uk = Country.objects.get(iso='GB')

data = simplejson.load(open('../data/edinburgh2010.json'))
for d in data:
    if d['festival'] != 'fringe': continue
    if d['main_class'] not in ('Childrens Shows', 'Dance and Physical Theatre', 'Musicals & Operas', 'Theatre'): continue
    venue = add_theatre(d['venue_desc'], 'Edinburgh')
    venue.description = d['venue_info']
    venue.address = d['venue_addr']
    venue.postcode = d['postcode']
    venue.country = uk
    venue.latitude = d['event_latitude']
    venue.longitude = d['event_longitude']
    venue.save()

    event = {
        'id': d['id'],
        'url': d['event_url'],
        'title': d['event_desc'],
        'desc': d['event_info'],
        'code': d['event_code'],
        'category': d['main_class'],
        'min_price': d['min_seat_price'],
        'start': datetime.fromtimestamp(int(d['start_timestamp'])).date().isoformat(),
        'end': datetime.fromtimestamp(int(d['end_timestamp'])).date().isoformat(),
    }

    title = re.sub('^(A|An|The) (.*)$', r'\2, \1', event['title'])
    try:
        play = Play.objects.get(title__iexact=title, authors=None)
    except:
        play = Play(title=title)
        play.save()

    production = Production(
        play = play,
        source = '<a href="http://projects.festivalslab.com/2010/">festivalslab</a> (<a href="%s"><s>edfringe</s></a>) <!-- %s %s -->' % (event['url'], event['id'], event['code']),
        description = event['desc'],
    )
    production.save()

    pp = ProductionPlace.objects.get_or_create(production=production, place=venue, start_date=event['start'], end_date=event['end'])

