import re
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect, Http404, HttpResponse
from django.urls import reverse
from django.db import IntegrityError
from django.contrib import messages

from common.models import AlertLocal
from places.models import Place
from people.models import Person
from productions.models import Production, ProductionCompany
from plays.models import Play
from shortcuts import check_url, UnmatchingSlugException
from utils import base32_to_int

#@login_required
#def alert(request, latlon, type):
#    m = re.match('\s*([-\d.]+)\s*,\s*([-\d.]+)\s*$', latlon)
#    if not m:
#        raise Http404
#    lat, lon = m.groups()
#    places = Place.objects.around(float(lat), float(lon))
#
#    if type == 'add':
#        alert = AlertLocal(user=request.user, latitude=lat, longitude=lon)
#        try:
#            alert.save()
#        except IntegrityError, e:
#            if e.args[0] != 1062: # Duplicate
#                raise
#        messages.success(request, u"Your alert has been added.")
#    elif type == 'remove':
#        AlertLocal.objects.filter(user=request.user, latitude=lat, longitude=lon).delete()
#        messages.success(request, u"Your alert has been removed.")
#
#    url = reverse('search-around', args=(latlon,))
#    if request.GET.get('name', ''):
#        url += '?name=%s' % request.GET['name']
#    return HttpResponseRedirect(url)

type_dict = {
    'play': Play,
    'place': Place,
    'person': Person,
    'production': Production,
    'company': ProductionCompany,
}

def api_flickr(request, type, id):
    if type in type_dict:
        obj_type = type_dict[type]
    else:
        raise Http404

    try:
        object = check_url(obj_type, id)
    except UnmatchingSlugException, e:
        url = '/api/%s/%s/flickr' % (type, e.args[0].id)
        return HttpResponsePermanentRedirect(url)

    return HttpResponse('%s' % object)

