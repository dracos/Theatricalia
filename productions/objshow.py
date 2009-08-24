from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from shortcuts import render
from models import Production, Part
from plays.models import Play
from places.models import Place
from people.models import Person
from aggregates import Concatenate

#def productions_past(places):
#    o = Production.objects.filter(
#        Q(place__end_date__lt=datetime.now) | Q(place__end_date='', place__press_date__lt=datetime.now),
#        place__place__in=places,
#    )
#    return o.order_by('-IFNULL(productions_place.press_date, IF(productions_place.end_date!="", productions_place.end_date, productions_place.start_date))')
#
#def productions_future(places):
#    return Production.objects.filter(
#        Q(place__end_date__gte=datetime.now) | Q(place__end_date='', place__press_date__gte=datetime.now),
#        place__place__in=places,
#    ).order_by('place__start_date', 'place__press_date')

# object is Place, Person, or Play
# type will be blank, or 'places' for multiple place search
def productions_filter(object, type, date_filter):
    if isinstance(object, Place) or isinstance(object, Person) or isinstance(object, Play):
        return object.productions.filter(date_filter)
    elif type=='places':
        return Production.objects.filter(date_filter, place__place__in=object)
    raise Exception, 'Strange call to productions_filter'

def productions_past(object, type):
    o = productions_filter(object, type, 
        Q(place__end_date__lt=datetime.now) | Q(place__end_date='', place__press_date__lt=datetime.now)
    )
    if isinstance(object, Person):
        o = o.annotate(Concatenate('part__role'))
    return o.order_by('-IFNULL(productions_place.press_date, IF(productions_place.end_date!="", productions_place.end_date, productions_place.start_date))')

def productions_future(object, type):
    o = productions_filter(object, type, 
        Q(place__end_date__gte=datetime.now) | Q(place__end_date='', place__press_date__gte=datetime.now)
    )
    return o.order_by('place__start_date', 'place__press_date')
    #.order_by('-IFNULL(press_date, IF(productions_production.end_date!="", productions_production.end_date, productions_production.start_date))')

def productions_list(request, object, dir, template, context={}):
    """Given an object, such as a Person, Place, or Play, return a page of productions for it."""

    type = ''
    if not (isinstance(object, Place) or isinstance(object, Person) or isinstance(object, Play)):
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

