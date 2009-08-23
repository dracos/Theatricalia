import string
from datetime import datetime
from shortcuts import render, check_url, UnmatchingSlugException
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from models import Person, first_letters
from forms import PersonEditForm
from photos.forms import PhotoForm
from productions.time import productions_list, productions_for
from django.core import serializers

def person_productions(request, person_id, person, type):
    try:
        person = check_url(Person, person_id, person)
    except UnmatchingSlugException, e:
        return HttpResponseRedirect(e.args[0].get_absolute_url())
    return productions_list(request, person, type, 'people/production_list.html')

def person(request, person_id, person):
    try:
        person = check_url(Person, person_id, person)
    except UnmatchingSlugException, e:
        return HttpResponseRedirect(e.args[0].get_absolute_url())
    past, future = productions_for(person)
    plays = person.plays.all()
    photo_form = PhotoForm(person)
    return render(request, 'people/person.html', {
        'person': person,
        'past': past,
        'future': future,
        'plays': plays,
        'photo_form': photo_form,
    })

def person_js(request, person_id, person):
    try:
        person = check_url(Person, person_id, person)
    except UnmatchingSlugException, e:
        return HttpResponseRedirect(e.args[0].get_absolute_url())
    response = HttpResponse()
    serializers.serialize("json", [ person ], ensure_ascii=False, stream=response)
    return response

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

