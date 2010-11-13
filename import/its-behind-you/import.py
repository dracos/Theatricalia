#!/usr/bin/python

import os, sys, re, time

for i in range(3, 0, -1):
    sys.path.append('../' * i)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings' 

from django.core.files.base import ContentFile

from plays.models import Play
from productions.models import Production, Part, ProductionCompany
from productions.models import Place as ProductionPlace
from people.models import Person
from photos.models import Photo

from functions import *
from plays2009 import *

real_run()

for venue in theatres:
    if "," in venue:
        name, town = venue.rsplit(',', 1)
        location = add_theatre(name, town)
    else:
        location = add_theatre(venue)
    theatres[venue] = location

for production in plays:
    title = production['title']
    log("Production of %s" % title)
    play = add_play(title, force_insert=True)

    company = None
    producer = production['producer']
    if producer:
        if dry_run():
            company = ProductionCompany(name=producer)
        else:
            company, created = ProductionCompany.objects.get_or_create(name=producer)

    description = production['description']
    source = '<a href="%s">its-behind-you.com</a>' % production['source']
    production_obj = Production(
        play = play,
        company = company,
        description = description,
        source = source,
    )
    if not dry_run():
        production_obj.save()

    if production['titleImg']:
        add_photo(production['titleImg'], production_obj, 'Title')

    for p in production['pictures']:
        add_photo(p, production_obj, 'Handbill')

    dates = production['dates']
    for d in dates:
        start_date, end_date = d[0]
        place = d[1]
        location = theatres[place]
        log('  %s %s   %s' % (start_date, end_date, location))
        if not dry_run():
            ProductionPlace.objects.get_or_create(production=production_obj, place=location, start_date=start_date, end_date=end_date)

    cast = production['cast']
    for name in cast:
        m = re.match('(.*) (.*?)$', name)
        if m:
            first_name, last_name = m.group(1), m.group(2)
        else:
            first_name, last_name = u'', name

        log('  Actor: ' + first_name + ' ' + last_name)
        if not dry_run():
            try:
                person, created = Person.objects.get_or_create(first_name=first_name, last_name=last_name)
            except:
                person = Person(first_name=first_name, last_name=last_name)
                person.save()
            Part.objects.get_or_create(production=production_obj, person=person, cast=True)
            if name in castLinks:
                person.web = castLinks[name]
                person.save()

