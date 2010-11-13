import os, sys
sys.path.insert(0, '../..')
sys.path.insert(0, '..')
os.environ['DJANGO_SETTINGS_MODULE'] = 'theatricalia.settings'

import re
from plays.models import Play
from utils import int_to_base32

plays = Play.objects.filter(title__istartswith='NT 2000: ')

for p in plays:
    without = p.title.replace('NT 2000: ', '')
    without = re.sub('^(A|An|The) (.*)', r'\2, \1', without)
    matches = Play.objects.filter(title=without)
    if len(matches)==1 and list(p.authors.all()) != list(matches[0].authors.all()):
        print int_to_base32(matches[0].id), int_to_base32(p.id), '|', matches[0].title, ' = ', p.title
        print '  ', p.authors.all()[0].id, matches[0].authors.all()[0].id
