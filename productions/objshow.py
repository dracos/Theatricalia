from datetime import datetime
from functools import partial
from django.core.paginator import Paginator, InvalidPage
from django.db.models import Q, Max, Min, Case, When, F
from django.db.models.functions import Coalesce
# from django.db.models.expressions import RawSQL
from django.http import Http404
from django.shortcuts import render
from .models import Production, Part, ProductionCompany
from plays.models import Play
from places.models import Place
from people.models import Person
from aggregates import Concatenate
from fields import ApproximateDateField


# object is Place, Person, Play, or ProductionCompany
# type will be blank, or 'places' for multiple place search
def productions_filter(object, type, date_filter):
    o = None
    now = datetime.now()

    if isinstance(object, Place):
        o = object.productions_here
        annotate_extra = ''
        filter_extra = False
    elif isinstance(object, Person) or isinstance(object, Play) or isinstance(object, ProductionCompany):
        o = object.productions
        annotate_extra = 'place__'
        filter_extra = False
    elif type == 'places':
        o = Production.objects
        annotate_extra = 'place__'
        filter_extra = True
    else:
        raise Exception('Strange call to productions_filter')

    end_date_field = f"{annotate_extra}end_date"
    press_date_field = f"{annotate_extra}press_date"
    start_date_field = f"{annotate_extra}start_date"
    o = o.annotate(
        max_end_date=Max(end_date_field),
        max_press_date=Max(press_date_field),
        max_start_date=Max(start_date_field)
    )
    filter = (~Q(max_end_date='') & Q(max_end_date__lt=now)) | Q(max_end_date='', max_press_date__lt=now) | Q(max_end_date='', max_press_date__isnull=True, max_start_date__lt=now)
    if filter_extra:
        if date_filter == 'past':
            o = o.filter(filter, place__place__in=object)
        else:
            o = o.exclude(filter).filter(place__place__in=object)
    else:
        if date_filter == 'past':
            o = o.filter(filter).distinct()
        else:
            o = o.exclude(filter).distinct()

    if isinstance(object, Person):
        o = o.annotate(part__role__concatenate=Concatenate('part__role', distinct=True))

    if date_filter == 'past':
        return o.annotate(best_date=Min(Coalesce(press_date_field, Case(When(**{end_date_field: ""}, then=F(start_date_field)), default=F(end_date_field)), output_field=ApproximateDateField()))).order_by('-best_date')
        # return o.annotate(best_date=Min(RawSQL('IFNULL(productions_place.press_date, IF(productions_place.end_date!="", productions_place.end_date, productions_place.start_date))', ()))).order_by('-best_date')
    else:
        return o.order_by(start_date_field, press_date_field)


def _prods_one_way(fltr, object, sort_order):
    qs = fltr(object)
    if isinstance(object, Place):
        # Loop through the children and include their productions also with UNION
        for child in object.children.all():
            qs = qs.union(fltr(child))
        # Need to do the sort again at the end after doing this
        qs = qs.order_by(*sort_order)
    return qs


def productions_past(object, type):
    fltr = partial(productions_filter, type=type, date_filter='past')
    return _prods_one_way(fltr, object, ('-best_date',))


def productions_future(object, type):
    fltr = partial(productions_filter, type=type, date_filter='future')
    return _prods_one_way(fltr, object, ('start_date', 'press_date'))


def productions_list(request, object, dir, template, context={}):
    """Given an object, such as a Person, Place, or Play, return a page of productions for it."""

    type = ''
    if not (isinstance(object, Place) or isinstance(object, Person) or isinstance(object, Play) or isinstance(object, ProductionCompany)):
        type = 'places'  # Assume it's around search at the mo

    if dir == 'future':
        paginator = Paginator(productions_future(object, type), 50, orphans=4)
        dir_str = 'Current & Upcoming productions'
    elif dir == 'past':
        paginator = Paginator(productions_past(object, type), 50, orphans=4)
        dir_str = 'Past productions'
    elif dir == 'parts':
        paginator = Paginator(Part.objects.search(object), 50, orphans=4)
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
    future_page = Paginator(productions_future(object, type), 50, orphans=4).page(1)
    past_page = Paginator(productions_past(object, type), 50, orphans=4).page(1)
    return past_page, future_page
