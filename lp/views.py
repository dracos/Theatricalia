import datetime
import dateutil.parser
import hashlib
import random

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

#from productions.models import Place
from photos.models import Photo

def generate(request, date=None, testing=False):
    if testing:
        date = datetime.datetime.now()
    # TODO Do something with the date - random production on date, though quite tricky?

    if not testing and not date.weekday() == 3:
        return HttpResponse("No content", status=204)

    if testing:
        random = Photo.objects.filter(id=1910)
    else:
        random = Photo.objects.exclude(id__gte=149, id__lte=159).filter(content_type=22).order_by('?')[:1]
    if not random:
        return HttpResponse("No content", status=204)
    production = random[0].content_object
    context = {
        'photo': random[0],
        'production': production
    }
    response = render(request, 'lp/day.html', context)
    response['ETag'] = '"%s"' % hashlib.sha224(str(production.id)).hexdigest()
    return response

def edition(request):
    if request.GET.get('test') == 'true':
        response = HttpResponse("Testing success " * 50)
        response['ETag'] = '"Testing"'
        return response

    if not request.GET.get('local_delivery_time',False):
        return HttpResponse("Error: No local_delivery_time was provided", status=400)
        
    date = dateutil.parser.parse(request.GET['local_delivery_time'])
    return generate(request, date=date)

def sample(request):
    return generate(request, testing=True)

def meta_json(request):
    return HttpResponseRedirect('/static/lp/meta.json')

def icon(request):
    return HttpResponseRedirect('/static/lp/icon.png')
