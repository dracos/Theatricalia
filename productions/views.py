import re
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from utils import base32_to_int, unique_slugify
from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory, inlineformset_factory
from django.contrib.comments.views.comments import post_comment
from django.http import Http404, HttpResponseRedirect
from shortcuts import render, check_url
from models import Production, Part, Place as ProductionPlace
from forms import ProductionForm, PartForm, PlaceForm
from plays.models import Play
from places.models import Place
from photos.forms import PhotoForm
from people.models import Person
from aggregates import Concatenate

def productions_past(object):
    o = object.productions.filter(
        Q(place__end_date__lt=datetime.now) | Q(place__end_date='', place__press_date__lt=datetime.now)
    )
    if isinstance(object, Person):
        o = o.annotate(Concatenate('part__role'))
    return o.order_by('-IFNULL(productions_place.press_date, IF(productions_place.end_date!="", productions_place.end_date, productions_place.start_date))')

def productions_future(object):
    return object.productions.filter(
        Q(place__end_date__gte=datetime.now) | Q(place__end_date='', place__press_date__gte=datetime.now)
    #).order_by('-IFNULL(press_date, IF(productions_production.end_date!="", productions_production.end_date, productions_production.start_date))')
    ).order_by('place__start_date', 'place__press_date')

#def production_add_parts(person, *pages):
#    production_ids = []
#    for page in pages:
#        production_ids += [ x.id for x in page.object_list ]
#    parts = Part.objects.filter(production__in=production_ids, person=person)
#    parts_for_production = {}
#    for p in parts:
#        parts_for_production.setdefault(p.production, []).append(p.role_or_unknown())
#    for page in pages:
#        for p in page.object_list:
#            p.their_parts = parts_for_production[p]

def production_list(request, object, type, template):
    """Given an object, such as a Person, Place, or Play, return a page of productions for it."""
    if type == 'future':
        paginator = Paginator(productions_future(object), 10, orphans=2)
    elif type == 'past':
        paginator = Paginator(productions_past(object), 10, orphans=2)

    page = request.GET.get('page', 1)
    try:
        page_number = int(page)
    except ValueError:
        raise Http404
    try:
        page_obj = paginator.page(page_number)
    except InvalidPage:
        raise Http404

    #if isinstance(object, Person):
    #    production_add_parts(object, page_obj)

    return render(request, template, {
        'type': type=='past' and 'Past productions' or 'Current & Upcoming productions',
        'object': object,
        'paginator': paginator,
        'page_obj': page_obj,
    })

def object_productions(object):
    """Given an object, such as a Person, Place, or Play, return the closes
       past/future productions for that object. If it's a Person, also include
       the Part(s) they played."""
    future_page = Paginator(productions_future(object), 10, orphans=2).page(1)
    past_page = Paginator(productions_past(object), 10, orphans=2).page(1)
    #if isinstance(object, Person):
        #production_add_parts(object, past_page, future_page)
    return past_page, future_page

def check_parameters(play, production_id):
    production_id = base32_to_int(production_id)
    production = get_object_or_404(Production, id=production_id)

    play = get_object_or_404(Play, slug=play)
    if play != production.play:
        raise Http404()
    return production

def production(request, play, production_id):
    production = check_parameters(play, production_id)
    photo_form = PhotoForm(production)
    production_form = ProductionForm(instance=production)

    ProductionPlaceFormSet = inlineformset_factory( Production, ProductionPlace, extra=1, form=PlaceForm )
    formset = ProductionPlaceFormSet(
        data = request.POST or None,
        prefix = 'place',
        instance = production,
    )

    return render(request, 'production.html', {
        'production': production,
        'production_form': production_form,
        'production_formset': formset,
        'cast': production.part_set.filter(cast=True).order_by('order', 'role'),
        'crew': production.part_set.filter(cast=False).order_by('order', 'role'),
        'photo_form': photo_form,
    })

def by_company(request, production):
    pass

def part_add(name):
    first_name, last_name = name.split(None, 1)
    slug = unique_slugify(Person, '%s %s' % (first_name, last_name))
    new_person = Person(first_name=first_name, last_name=last_name, slug=slug)
    new_person.save()
    return new_person

@login_required
def part_edit(request, play, production_id, part_id):
    production = check_parameters(play, production_id)

    part = get_object_or_404(Part, id=part_id)
    if part.production != production:
        raise Http404()

    part_form = PartForm(
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
def production_edit(request, play, production_id):
    production = check_parameters(play, production_id)
    production_form = ProductionForm(data=request.POST or None, instance=production)

    ProductionPlaceFormSet = inlineformset_factory( Production, ProductionPlace, extra=1, form=PlaceForm )
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
def production_edit_cast(request, play, production_id):
    """For picking someone to edit, or adding a new Part"""
    production = check_parameters(play, production_id)
    part_form = PartForm(request.POST or None)

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

def _production_add(request, play=None, place=None):
    if not play and not place:
        raise Exception, 'Must not get here without something!'

    initial = {}
    if play: initial['play'] = play.id
    production_form = ProductionForm(
        data = request.POST or None,
        initial = initial,
    )

    ProductionPlaceFormSet = modelformset_factory( ProductionPlace, exclude=('production'), form=PlaceForm )
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
def production_add(request, play):
    play = get_object_or_404(Play, slug=play)
    return _production_add(request, play=play)

@login_required
def add_from_place(request, place_id, place):
    place = check_url(Place, place_id, place)
    return _production_add(request, place=place)

def post_comment_wrapper(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/tickets')
    return post_comment(request)
