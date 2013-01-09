import string
from datetime import datetime

from django.views.generic.list_detail import object_list
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django.views.decorators.cache import cache_page

from common.models import Alert
from forms import PlaceForm
from models import Place
from shortcuts import render, check_url, UnmatchingSlugException
from productions.objshow import productions_list, productions_for
from productions.models import Production, Production_Companies, Place as ProductionPlace, Part
from people.models import Person
from photos.forms import PhotoForm

def place_short_url(request, place_id):
    try:
        place = check_url(Place, place_id)
    except UnmatchingSlugException, e:
        place = e.args[0]
    return HttpResponsePermanentRedirect(place.get_absolute_url())

def place_productions(request, place_id, place, type):
    try:
        place = check_url(Place, place_id, place)
    except UnmatchingSlugException, e:
        return HttpResponsePermanentRedirect(e.args[0].get_absolute_url())
    return productions_list(request, place, type, 'places/production_list.html')

def productions(request, place_id, place):
    try:
        place = check_url(Place, place_id, place)
    except UnmatchingSlugException, e:
        return HttpResponsePermanentRedirect(e.args[0].get_absolute_url())

    productions = Production.objects.filter(places=place).order_by('play__title').select_related('play')
    productions_dict = dict([(obj.id, obj) for obj in productions])

    companiesM2M = Production_Companies.objects.filter(production__in=productions).select_related('productioncompany')
    m2m = {}
    for c in companiesM2M:
        m2m.setdefault(c.production_id, []).append( c.productioncompany )
    for p in productions:
        p._companies = m2m.get(p.id, [])

    placeM2M = ProductionPlace.objects.filter(production__in=productions).order_by('start_date', 'press_date', 'end_date')
    m2m = {}
    for p in placeM2M:
        m2m.setdefault(p.production_id, []).append( p )
    for p in productions:
        p._place_set = m2m.get(p.id, [])

    return render(request, 'places/productions.html', {
        'productions': productions,
        'place': place,
    })

def people(request, place_id, place):
    try:
        place = check_url(Place, place_id, place)
    except UnmatchingSlugException, e:
        return HttpResponsePermanentRedirect(e.args[0].get_absolute_url())

    people = Person.objects.filter(productions__places=place).distinct().order_by('last_name', 'first_name')
    productionsM2M = Part.objects.filter(production__places=place, person__in=people).select_related('production')
    m2m = {}
    for p in productionsM2M:
        m2m.setdefault(p.person_id, []).append( p.production )
    for p in people:
        p._productions = m2m.get(p.id, [])

    return render(request, 'places/people.html', {
        'people': people,
        'place': place,
    })

@login_required
def place_edit(request, place_id, place):
    try:
        place = check_url(Place, place_id, place)
    except UnmatchingSlugException, e:
        return HttpResponsePermanentRedirect(e.args[0].get_absolute_url())

    form = PlaceForm(request.POST or None, instance=place)
    if request.method == 'POST':
        if request.POST.get('disregard'):
            request.user.message_set.create(message=u"All right, we\u2019ve ignored any changes you made.")
            return HttpResponseRedirect(place.get_absolute_url())
        if form.is_valid():
            form.save()
            request.user.message_set.create(message="Your changes have been stored; thank you.")
            return HttpResponseRedirect(place.get_absolute_url())

    return render(request, 'places/place_edit.html', {
        'place': place,
        'form': form,
    })

def place(request, place_id, place):
    try:
        place = check_url(Place, place_id, place)
    except UnmatchingSlugException, e:
        return HttpResponsePermanentRedirect(e.args[0].get_absolute_url())
    past, future = productions_for(place)
    photo_form = PhotoForm(place)
    alert = place.alerts.filter(user=request.user)
    return render(request, 'place.html', {
        'place': place,
        'past': past,
        'future': future,
        'photo_form': photo_form,
        'alert': alert,
    })

@login_required
def place_alert(request, place_id, place, type):
    try:
        place = check_url(Place, place_id, place)
    except UnmatchingSlugException, e:
        return HttpResponsePermanentRedirect(e.args[0].get_absolute_url())

    if type == 'add':
        alert = Alert(user=request.user, content_object=place)
        try:
            alert.save()
        except IntegrityError, e:
            if e.args[0] != 1062: # Duplicate
                raise
        request.user.message_set.create(message=u"Your alert has been added.")
    elif type == 'remove':
        place.alerts.filter(user=request.user).delete()
        request.user.message_set.create(message=u"Your alert has been removed.")

    return HttpResponseRedirect(place.get_absolute_url())

@cache_page(60*5)
def list_places(request, letter='a'):
    if letter == '0':
        places = Place.objects.filter(name__regex=r'^[0-9]')
        letter = '0-9'
    elif letter == '*':
        places = Place.objects.exclude(name__regex=r'^[A-Za-z0-9]')
        letter = 'Symbols'
    else:
        places = Place.objects.filter(name__istartswith=letter)
        letter = letter.upper()
    letters = list(string.ascii_uppercase)
    return object_list(request, queryset=places, extra_context={ 'letter': letter, 'letters': letters })

