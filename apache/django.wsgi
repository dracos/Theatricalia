#!/usr/local/bin/python

import os, sys

# Custom paths for location of Django and project - think this should work.
sys.path.insert(0, "/guest/matthew/web/theatricalia/ext")
sys.path.insert(0, "/guest/matthew/web/theatricalia")

os.environ['DJANGO_SETTINGS_MODULE'] = 'theatricalia.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
