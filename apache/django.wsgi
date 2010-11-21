#!/usr/local/bin/python

import os, sys

script_dir = os.path.dirname(__file__)
project_dir = os.path.abspath(os.path.join(script_dir, '..'))
vhost_dir = os.path.abspath(os.path.join(project_dir, '..'))

# Custom paths for location of Django and project - think this should work.
for path in (script_dir, project_dir, vhost_dir):
    if path not in sys.path:
        sys.path.insert(0, path)

if 'staging' in script_dir:
    import wsgi_monitor
    wsgi_monitor.start(interval=1.0)
os.environ['DJANGO_SETTINGS_MODULE'] = 'theatricalia.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
