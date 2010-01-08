from django.conf import settings
from django.db import models

#for app in models.get_apps():
#    exec("from %s import *" % app.__name__)
for m in models.loading.get_models():
    exec "from %s import %s" % (m.__module__, m.__name__)

from utils import *

import os
import sys
import datetime
