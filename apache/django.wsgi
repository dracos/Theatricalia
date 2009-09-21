#!/usr/local/bin/python

import os, sys

# Custom paths for location of Django and project - think this should work.
sys.path.insert(0, "/srv/theatricalia.com/theatricalia") # For my imports
sys.path.insert(0, "/srv/theatricalia.com") # For everything else

os.environ['DJANGO_SETTINGS_MODULE'] = 'theatricalia.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
