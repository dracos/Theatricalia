#!/usr/bin/python

import re, os, sys, csv
from datetime import datetime
sys.path.append('../../')
sys.path.append('../')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from functions import add_theatre, real_run
from plays.models import Play
from productions.models import Production, Part, Place as ProductionPlace, ProductionCompany, Production_Companies
from people.models import Person
from places.models import Place
from countries.models import Country

#real_run()

uk = Country.objects.get(iso='GB')

file = csv.reader(open('../data/festivalfm/performer.csv'), quotechar="'")
performer = {}
for row in file:
    performer[row[0]] = row[1]

file = csv.reader(open('../data/festivalfm/venue.csv'), quotechar="'")
venue_by_id = {}
for row in file:
    id, name, address, postcode, latitude, longitude, description, access = row
    venue = add_theatre(name, 'Edinburgh')
    venue.country = uk
    if not venue.address and address: venue.address = address
    if not venue.postcode and postcode: venue.postcode = postcode
    if not venue.latitude and float(latitude): venue.latitude = latitude
    if not venue.longitude and float(longitude): venue.longitude = longitude
    if not venue.description and description: venue.description = '%s\n\n%s' % (description, access)
    venue.save()
    venue_by_id[id] = venue

file = csv.reader(open('../data/festivalfm/show.csv'), quotechar="'")
show = {}
for row in file:
    if row[9] != '1': raise Exception, row # Fringe only
    if row[2] not in ('Theatre', 'Festival Opera', 'Musicals and Operas', 'Children\'s Shows', 'Dance and Physical Theatre'):
        continue
    row.append('9999-12-31') # Start date
    row.append('0000-00-00') # End date
    row[3] = venue_by_id[row[3]]
    row[4] = performer[row[4]]
    show[row[0]] = row

file = csv.reader(open('../data/festivalfm/performance.csv'), quotechar="'")
for row in file:
    show_id, start, end = row[1:4]
    if show_id not in show: continue
    if start < show[show_id][10]: show[show_id][10] = start[:10]
    if end   > show[show_id][11]: show[show_id][11] = end[:10]

for row in show.values():
    if row[10] == '9999-12-31': row[10] = '2008-08-00'
    if row[11] == '0000-00-00': row[11] = '2008-08-00'
    id, title, category, venue, performer, description, warning, agerange, url, festival, start, end = row
    print id, title, performer
    if agerange != '0' or url != '' or festival != '1': raise Exception, row

    title = re.sub('^(A|An|The) (.*)$', r'\2, \1', title)
    try:
        play = Play.objects.get(title__iexact=title, authors=None)
    except:
        play = Play(title=title)
        play.save()

    try:
        Production.objects.get(
            source = '<a href="http://festivalfm.net/">FestivalFM</a> <!-- %s -->' % id,
        )
        print "  Already exists!"
        continue
    except:
        pass

    production = Production(
        play = play,
        source = '<a href="http://festivalfm.net/">FestivalFM</a> <!-- %s -->' % id,
        description = description,
    )
    production.save()

    if performer:
        try:
            company = ProductionCompany.objects.filter(name=performer)[0]
        except:
            company, created = ProductionCompany.objects.get_or_create(name=performer)
        Production_Companies.objects.get_or_create(production=production, productioncompany=company)

    ProductionPlace.objects.get_or_create(production=production, place=venue, start_date=start, end_date=end)

