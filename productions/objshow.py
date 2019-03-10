from datetime import datetime
from django.core.paginator import Paginator, InvalidPage
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render
from models import Production, Part, ProductionCompany
from plays.models import Play
from places.models import Place
from people.models import Person
from aggregates import Concatenate

# object is Place, Person, Play, or ProductionCompany
# type will be blank, or 'places' for multiple place search
def productions_filter(object, type, date_filter):
    o = None
    now = datetime.now()
    if isinstance(object, Place):
        filter = ( ~Q(end_date='') & Q(end_date__lt=now) ) | Q(end_date='', press_date__lt=now) | Q(end_date='', press_date__isnull=True, start_date__lt=now)
        if date_filter == 'past':
            o = object.productions_here.filter(filter).distinct()
        else:
            o = object.productions_here.exclude(filter).distinct()
    elif isinstance(object, Person) or isinstance(object, Play) or isinstance(object, ProductionCompany):
        filter = ( ~Q(place__end_date='') & Q(place__end_date__lt=now) ) | Q(place__end_date='', place__press_date__lt=now) | Q(place__end_date='', place__press_date__isnull=True, place__start_date__lt=now)
        if date_filter == 'past':
            o = object.productions.filter(filter).distinct()
        else:
            o = object.productions.exclude(filter).distinct()
    elif type=='places':
        filter = ( ~Q(place__end_date='') & Q(place__end_date__lt=now) ) | Q(place__end_date='', place__press_date__lt=now) | Q(place__end_date='', place__press_date__isnull=True, place__start_date__lt=now)
        if date_filter == 'past':
            o = Production.objects.filter(filter, place__place__in=object)
        else:
            o = Production.objects.exclude(filter).filter(place__place__in=object)
    else:
        raise Exception, 'Strange call to productions_filter'
    if isinstance(object, Person):
        o = o.annotate(part__role__concatenate=Concatenate('part__role'))

    if date_filter == 'past':
        if isinstance(object, Person):
            return o.extra(select={'best_date': 'IFNULL(press_date, IF(productions_place.end_date!="", productions_place.end_date, productions_place.start_date))'}).order_by('-best_date')
        else:
            return o.extra(select={'best_date': 'IFNULL(press_date, IF(end_date!="", end_date, start_date))'}).order_by('-best_date')
    else:
        if isinstance(object, Place):
            return o.order_by('start_date', 'press_date')
        else:
            return o.order_by('place__start_date', 'place__press_date')
    #.order_by('-IFNULL(press_date, IF(productions_production.end_date!="", productions_production.end_date, productions_production.start_date))')

def productions_past(object, type):
    return productions_filter(object, type, 'past')

def productions_future(object, type):
    return productions_filter(object, type, 'future')

def productions_list(request, object, dir, template, context={}):
    """Given an object, such as a Person, Place, or Play, return a page of productions for it."""

    type = ''
    if not (isinstance(object, Place) or isinstance(object, Person) or isinstance(object, Play) or isinstance(object, ProductionCompany)):
        type = 'places' # Assume it's around search at the mo

    if dir == 'future':
        paginator = Paginator(productions_future(object, type), 10, orphans=2)
        dir_str = 'Current & Upcoming productions'
    elif dir == 'past':
        paginator = Paginator(productions_past(object, type), 10, orphans=2)
        dir_str = 'Past productions'
    elif dir == 'parts':
        paginator = Paginator(Part.objects.search(object), 10, orphans=2)
        dir_str = u'Parts containing \u201c%s\u201d' % object

    page = request.GET.get('page', 1)
    try:
        page_number = int(page)
    except ValueError:
        raise Http404
    try:
        page_obj = paginator.page(page_number)
    except InvalidPage:
        raise Http404

    context.update({
        'type': dir_str,
        'object': object,
        'paginator': paginator,
        'page_obj': page_obj,
    })
    return render(request, template, context)

def productions_for(object, type=''):
    """Given an object, such as a Person, Place, or Play, return the closes
       past/future productions for that object. If it's a Person, also include
       the Part(s) they played."""
    future_page = Paginator(productions_future(object, type), 10, orphans=2).page(1)
    past_page = Paginator(productions_past(object, type), 10, orphans=2).page(1)
    return past_page, future_page

