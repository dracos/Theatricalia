import string
from datetime import datetime

from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.db import IntegrityError
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.utils import simplejson

from shortcuts import render, check_url, UnmatchingSlugException
from utils import int_to_base32, base32_to_int
from common.models import Alert
from models import Person, first_letters
from forms import PersonEditForm
from photos.forms import PhotoForm
from productions.objshow import productions_list, productions_for, productions_past, productions_future

def person_productions(request, person_id, person, type):
    try:
        person = check_url(Person, person_id, person)
    except UnmatchingSlugException, e:
        return HttpResponseRedirect(e.args[0].get_absolute_url())
    return productions_list(request, person, type, 'people/production_list.html')

def person_short_url(request, person_id):
    person_id = base32_to_int(person_id)
    person = get_object_or_404(Person, id=person_id)
    return HttpResponsePermanentRedirect(person.get_absolute_url())

def person(request, person_id, person):
    try:
        person = check_url(Person, person_id, person)
    except UnmatchingSlugException, e:
        return HttpResponseRedirect(e.args[0].get_absolute_url())

    if person.productions.count() == 0:
        raise Http404()

    past, future = productions_for(person)
    plays = person.plays.all()
    photo_form = PhotoForm(person)
    alert = person.alerts.filter(user=request.user)
    same_name = Person.objects.filter(first_name=person.first_name, last_name=person.last_name).exclude(id=person.id)
    return render(request, 'people/person.html', {
        'person': person,
        'past': past,
        'future': future,
        'plays': plays,
        'photo_form': photo_form,
        'alert': alert,
        'same_name': same_name,
    })

def person_js(request, person_id, person):
    try:
        person = check_url(Person, person_id, person)
    except UnmatchingSlugException, e:
        return HttpResponseRedirect(e.args[0].get_absolute_url())
    plays = person.plays.all()

    past   = [ {'id': int_to_base32(p.id), 'desc': unicode(p) } for p in productions_past(person, '') ]
    future = [ {'id': int_to_base32(p.id), 'desc': unicode(p) } for p in productions_future(person, '') ]
    plays  = [ {'id': int_to_base32(p.id), 'title': unicode(p) } for p in person.plays.all() ]
    person = {
        'id': int_to_base32(person.id),
        'first_name': person.first_name,
        'last_name': person.last_name,
        'slug': person.slug,
        'bio': person.bio,
        'dob': person.dob,
        'died': person.died,
        'web': person.web,
        'imdb': person.imdb,
    }
    out = {
        'person': person,
        'past': past,
        'future': future,
        'plays': plays,
    }
    response = HttpResponse(mimetype='application/json')
    simplejson.dump(out, response, ensure_ascii=False)
    return response

@login_required
def person_alert(request, person_id, person, type):
    try:
        person = check_url(Person, person_id, person)
    except UnmatchingSlugException, e:
        return HttpResponseRedirect(e.args[0].get_absolute_url())

    if type == 'add':
        alert = Alert(user=request.user, content_object=person)
        try:
            alert.save()
        except IntegrityError, e:
            if e.args[0] != 1062: # Duplicate
                raise
        request.user.message_set.create(message=u"Your alert has been added.")
    elif type == 'remove':
        person.alerts.filter(user=request.user).delete()
        request.user.message_set.create(message=u"Your alert has been removed.")

    return HttpResponseRedirect(person.get_absolute_url())

@login_required
def person_edit(request, person_id, person):
    try:
        person = check_url(Person, person_id, person)
    except UnmatchingSlugException, e:
        return HttpResponseRedirect(e.args[0].get_absolute_url())

    form = PersonEditForm(data=request.POST or None, instance=person)
    if request.method == 'POST':
        if request.POST.get('disregard'):
            request.user.message_set.create(message=u"All right, we\u2019ve ignored any changes you made.")
            return HttpResponseRedirect(person.get_absolute_url())
        if form.is_valid():
            form.save()
            request.user.message_set.create(message="Your changes have been stored, thank you.")
            return HttpResponseRedirect(person.get_absolute_url())

    return render(request, 'people/person_edit.html', {
        'person': person,
        'form': form,
    })

def list(request, letter='a'):
    if letter == '0':
        people = Person.objects.filter(last_name__regex=r'^[0-9]')
        letter = '0-9'
    elif letter == '*':
        people = Person.objects.exclude(last_name__regex=r'^[A-Za-z0-9]')
        letter = 'Symbols'
    else:
        people = Person.objects.filter(last_name__istartswith=letter)
        letter = letter.upper()
    letters = [ x[0] for x in first_letters() if x[0]>='A' and x[0]<='Z' ]
    letters.sort()
    return object_list(request, queryset=people, paginate_by=30, extra_context={ 'letter': letter, 'letters': letters, 'request':request })

