#!/usr/bin/python

import os, sys, urllib
from os.path import basename

for i in range(3, 0, -1):
    sys.path.append('../' * i)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings' 

from django.core.files.base import ContentFile
from photos.models import Photo
from functions import *
from plays2009 import *
from pprint import pprint

for venue in theatres:
    if "," in venue:
        name, town = venue.rsplit(',', 1)
        location = add_theatre(name, town)
    else:
        location = add_theatre(venue)
    if 'links' in theatres[venue] and not location.url and not dry_run:
        location.url = theatres[venue]['links'].pop()[0]
        location.save()
    if 'logos' in theatres[venue] and not dry_run:
        file = theatres[venue]['logos'].pop()
        add_photo(file, location, 'Logo')

    theatres[venue]['id'] = location.id

pprint(theatres)

