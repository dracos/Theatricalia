#!/usr/bin/python

import os, sys, glob, re
import time
from datetime import datetime

sys.path.append('../../../')
sys.path.append('../../')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings' 

from plays.models import Play
from productions.models import Production, Part, ProductionCompany
from productions.models import Place as ProductionPlace
from people.models import Person
from places.models import Place

from data import *

for production in plays:
    start, end = production['dates']
    time.strptime('j F Y', start)
