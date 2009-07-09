from datetime import datetime
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.http import base36_to_int
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.contrib.comments.views.comments import post_comment
#from django.forms.models import modelformset_factory, inlineformset_factory, BaseInlineFormSet
from django.http import Http404, HttpResponseRedirect
from shortcuts import render
from models import Production, Part
from forms import ProductionEditForm, PartEditForm, PartAddForm, BasePartFormSet
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

def production(request, play, production_id):
    production_id = base36_to_int(production_id)
    production = get_object_or_404(Production, id=production_id)
    play = get_object_or_404(Play, slug=play)
    if play != production.play:
        raise Http404()
    photo_form = PhotoForm(production)
    return render(request, 'production.html', {
        'production': production,
        'cast': production.part_set.filter(cast=True).order_by('order', 'role'),
        'crew': production.part_set.filter(cast=False).order_by('order', 'role'),
        'photo_form': photo_form,
    })

def by_company(request, production):
    pass

@login_required
def production_edit(request, play, production_id):
    production_id = base36_to_int(production_id)
    production = get_object_or_404(Production, id=production_id)
    play = get_object_or_404(Play, slug=play)
    if play != production.play:
        raise Http404()

    production_form = ProductionEditForm(data=request.POST or None, instance=production, prefix='production', last_modified=production.last_modified)

    # Inline FormSet problems - seems ideal, but can't get person name
    # instead of <select> or ID number, plus can't get order right
    #PartFormSet = inlineformset_factory(Production, Part, extra=0, can_delete=False, form=PartEditForm, exclude='credit', formset=PartInlineFormSet)
    #parts_formset = PartFormSet(request.POST or None, instance=production, prefix='parts-existing')

    PartFormSet = formset_factory(PartEditForm, BasePartFormSet, extra=0)
    PartAddFormSet = formset_factory(PartAddForm)
    new_parts_formset = PartAddFormSet(request.POST or None, prefix='parts-new')

    if request.method == 'POST':
        parts_formset = PartFormSet(request.POST, prefix='parts-existing' )
        #form.save_with_log(request)
        #request.user.message_set.create(message="Your changes have been stored, thank you.")
        #return HttpResponseRedirect(person.get_absolute_url())
    else:
        parts = production.part_set.all().order_by('-cast', 'order', 'role')
        parts_list = []
        for part in parts:
            parts_list.append({
                'id': part.id,
                'person': part.person,
                'role': part.role,
                'cast': part.cast,
                'order': part.order,
                'start_date': part.start_date,
                'end_date': part.end_date,
            })
        parts_formset = PartFormSet( initial=parts_list, prefix='parts-existing' )

    return render(request, 'production_edit.html', {
        'form': production_form,
        'parts': parts_formset,
        'new_parts': new_parts_formset,
        'production': production,
    })

def post_comment_wrapper(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/tickets')
    return post_comment(request)
