import re
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.db import IntegrityError

from common.models import AlertLocal
from places.models import Place
from shortcuts import check_url, UnmatchingSlugException

@login_required
def alert(request, latlon, type):
    m = re.match('\s*([-\d.]+)\s*,\s*([-\d.]+)\s*$', latlon)
    if not m:
        raise Http404
    lat, lon = m.groups()
    places = Place.objects.around(float(lat), float(lon))

    if type == 'add':
        alert = AlertLocal(user=request.user, latitude=lat, longitude=lon)
        try:
            alert.save()
        except IntegrityError, e:
            if e.args[0] != 1062: # Duplicate
                raise
        request.user.message_set.create(message=u"Your alert has been added.")
    elif type == 'remove':
        AlertLocal.objects.filter(user=request.user, latitude=lat, longitude=lon).delete()
        request.user.message_set.create(message=u"Your alert has been removed.")

    url = reverse('search-around', args=(latlon,))
    if request.GET.get('name', ''):
        url += '?name=%s' % request.GET['name']
    return HttpResponseRedirect(url)

