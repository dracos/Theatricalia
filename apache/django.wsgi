#!/usr/local/bin/python

import os, sys

# Custom paths for location of Django and project - think this should work.
for path in ("/srv/theatricalia.com/theatricalia", "/srv/theatricalia.com"):
    if path not in sys.path:
        sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'theatricalia.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
