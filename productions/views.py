import re

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory, inlineformset_factory
from django.db import IntegrityError
from django.contrib.comments.views.comments import post_comment
from django.http import Http404, HttpResponseRedirect

from utils import base32_to_int, unique_slugify
from shortcuts import render, check_url
from models import Production, Part, Place as ProductionPlace, Visit
from forms import ProductionForm, ProductionFormNoJS, PartForm, PlaceForm, PlaceFormNoJS
from plays.models import Play
from places.models import Place
from photos.forms import PhotoForm
from people.models import Person

def check_parameters(play_id, play, production_id):
    production_id = base32_to_int(production_id)
    production = get_object_or_404(Production, id=production_id)

    play = check_url(Play, play_id, play)
    if play != production.play:
        raise Http404()
    return production

def production(request, play_id, play, production_id):
    production = check_parameters(play_id, play, production_id)
    photo_form = PhotoForm(production)
#    production_form = ProductionForm(instance=production)
#
#    ProductionPlaceFormSet = inlineformset_factory( Production, ProductionPlace, extra=1, form=PlaceForm )
#    formset = ProductionPlaceFormSet(
#        data = request.POST or None,
#        prefix = 'place',
#        instance = production,
#    )

    try:
        seen = production.visit_set.get(user=request.user)
    except:
        seen = None

    return render(request, 'production.html', {
        'production': production,
#        'production_form': production_form,
#        'production_formset': formset,
        'cast': production.part_set.filter(cast=True).order_by('order', 'role'),
        'crew': production.part_set.filter(cast=False).order_by('order', 'role'),
        'photo_form': photo_form,
        'seen': seen,
    })

@login_required
def production_seen(request, play_id, play, production_id, type):
    production = check_parameters(play_id, play, production_id)
    if type == 'add':
        alert = Visit(user=request.user, production=production)
        try:
            alert.save()
        except IntegrityError, e:
            if e.args[0] != 1062: # Duplicate
                raise
        request.user.message_set.create(message=u"Your visit has been recorded.")
    elif type == 'remove':
        Visit.objects.get(user=request.user, production=production).delete()
        request.user.message_set.create(message=u"Your visit has been removed.")

    return HttpResponseRedirect(production.get_absolute_url())


def by_company(request, production):
    pass

def part_add(name):
    first_name, last_name = name.split(None, 1)
    slug = unique_slugify(Person, '%s %s' % (first_name, last_name))
    new_person = Person(first_name=first_name, last_name=last_name, slug=slug)
    new_person.save()
    return new_person

@login_required
def part_edit(request, play_id, play, production_id, part_id):
    production = check_parameters(play_id, play, production_id)

    part = get_object_or_404(Part, id=part_id)
    if part.production != production:
        raise Http404()

    part_form = PartForm(
        editing = True,
        data = request.POST or None,
        instance = part,
        initial = { 'person': part.person } # To make form have name rather than ID
    )

    if request.method == 'POST':
        if request.POST.get('disregard'):
            request.user.message_set.create(message=u"All right, we\u2019ve ignored any changes you made.")
            return HttpResponseRedirect(production.get_edit_cast_url())
        if part_form.is_valid():
            if part_form.cleaned_data.get('person_choice') == 'new':
                part_form.cleaned_data['person'] = part_add(part_form.cleaned_data['person'])
            part_form.save()
            request.user.message_set.create(message="Your changes have been stored; thank you.")
            return HttpResponseRedirect(production.get_edit_cast_url())

    return render(request, 'productions/edit-part.html', {
        'id': part_id,
        'form': part_form,
        'production': production,
    })

@login_required
def production_edit(request, play_id, play, production_id):
    production = check_parameters(play_id, play, production_id)

    if request.GET.get('js', '1')=='1':
        production_form = ProductionForm
        place_form = PlaceForm
    else:
        production_form = ProductionFormNoJS
        place_form = PlaceFormNoJS

    production_form = production_form(data=request.POST or None, instance=production)

    ProductionPlaceFormSet = inlineformset_factory( Production, ProductionPlace, extra=1, form=place_form )
    formset = ProductionPlaceFormSet(
        data = request.POST or None,
        prefix = 'place',
        instance = production,
    )

    if request.method == 'POST':
        if request.POST.get('disregard'):
            request.user.message_set.create(message=u"All right, we\u2019ve ignored any changes you made.")
            return HttpResponseRedirect(production.get_absolute_url())
        if production_form.is_valid() and formset.is_valid():
            production_form.save()
            formset.save()
            request.user.message_set.create(message="Your changes have been stored; thank you.")
            return HttpResponseRedirect(production.get_absolute_url())

    return render(request, 'productions/edit.html', {
        'form': production_form,
        'formset': formset,
        'production': production,
    })

@login_required
def production_edit_cast(request, play_id, play, production_id):
    """For picking someone to edit, or adding a new Part"""
    production = check_parameters(play_id, play, production_id)
    part_form = PartForm(request.POST or None, editing=False)

    if request.method == 'POST':
        if part_form.is_valid():
            if part_form.cleaned_data.get('person_choice') == 'new':
                part_form.cleaned_data['person'] = part_add(part_form.cleaned_data['person'])
            part_form.cleaned_data['production'] = production
            part_form.save()
            request.user.message_set.create(message="Your new part has been added; thank you.")
            return HttpResponseRedirect(production.get_edit_cast_url())

    return render(request, 'productions/edit-parts.html', {
        'production': production,
        'form': part_form,
        'parts': production.part_set.order_by('-cast','order','role'),
    })

@login_required
def production_add(request, play=None, place=None):

    initial = {}
    if play: initial['play'] = play.id

    if request.GET.get('js', '1')=='1':
        production_form = ProductionForm
        place_form = PlaceForm
    else:
        production_form = ProductionFormNoJS
        place_form = PlaceFormNoJS

    production_form = production_form(data=request.POST or None, initial=initial)

    ProductionPlaceFormSet = modelformset_factory( ProductionPlace, form=place_form )
    formset = ProductionPlaceFormSet(
        data = request.POST or None,
        prefix = 'place',
        queryset = ProductionPlace.objects.none()
    )

    # Yucky, but no way to pass initial to a model formset XXX
    if place:
        formset.forms[0].initial['place'] = place.id

    if request.method == 'POST':
        if request.POST.get('disregard'):
            request.user.message_set.create(message=u"All right, we\u2019ve ignored what you had done.")
            if play: return HttpResponseRedirect(play.get_absolute_url())
            if place: return HttpResponseRedirect(place.get_absolute_url())
        if production_form.is_valid() and formset.is_valid():
            production = production_form.save()
            for form in formset.forms:
                form.cleaned_data['production'] = production
            formset.save()
            request.user.message_set.create(message="Your addition has been stored; thank you. If you know members of the cast or crew, please feel free to add them now.")
            return HttpResponseRedirect(production.get_edit_cast_url())

    return render(request, 'productions/add.html', {
        'place': place,
        'formset': formset,
        'play': play,
        'form': production_form,
    })

@login_required
def add_from_play(request, play_id, play):
    try:
        play = check_url(Play, play_id, play)
    except UnmatchingSlugException, e:
        return HttpResponseRedirect(e.args[0].get_absolute_url())
    return production_add(request, play=play)

@login_required
def add_from_place(request, place_id, place):
    place = check_url(Place, place_id, place)
    return production_add(request, place=place)

def post_comment_wrapper(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/tickets')
    return post_comment(request)
