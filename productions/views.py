import re
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from utils import base32_to_int, unique_slugify
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.contrib.comments.views.comments import post_comment
from django.http import Http404, HttpResponseRedirect
from shortcuts import render
from models import Production, Part
from forms import ProductionEditForm, PartForm
from plays.models import Play
from photos.forms import PhotoForm
from people.models import Person
from aggregates import Concatenate

def productions_past(object):
    return object.productions.filter(
        Q(end_date__lt=datetime.now) | Q(end_date='', press_date__lt=datetime.now)
    ).annotate(Concatenate('part__role')).order_by('-IFNULL(press_date, IF(productions_production.end_date!="", productions_production.end_date, productions_production.start_date))')

def productions_future(object):
    return object.productions.filter(
        Q(end_date__gte=datetime.now) | Q(end_date='', press_date__gte=datetime.now)
    #).order_by('-IFNULL(press_date, IF(productions_production.end_date!="", productions_production.end_date, productions_production.start_date))')
    ).order_by('start_date', 'press_date')

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
        paginator = Paginator(productions_future(object), 10)
    elif type == 'past':
        paginator = Paginator(productions_past(object), 10)

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
    future_page = Paginator(productions_future(object), 10).page(1)
    past_page = Paginator(productions_past(object), 10).page(1)
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
    production_form = ProductionEditForm(instance=production)

    return render(request, 'production.html', {
        'production': production,
        'production_form': production_form,
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
    production_form = ProductionEditForm(data=request.POST or None, instance=production)

    if request.method == 'POST':
        if request.POST.get('disregard'):
            request.user.message_set.create(message=u"All right, we\u2019ve ignored any changes you made.")
            return HttpResponseRedirect(production.get_absolute_url())
        if production_form.is_valid():
            production_form.save()
            request.user.message_set.create(message="Your changes have been stored; thank you.")
            return HttpResponseRedirect(production.get_absolute_url())

    return render(request, 'productions/edit.html', {
        'form': production_form,
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

def post_comment_wrapper(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/tickets')
    return post_comment(request)
