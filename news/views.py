import calendar
from django.views.generic import date_based
from models import Article

def setup_dict():
    return {
        'queryset': Article.objects.visible(),
        'date_field': 'created',
        'extra_context': {
            'all': Article.objects.all(),
        },
    }

def month(request, year, month):
    return date_based.archive_month(request, year=year, month=month, month_format='%B', **setup_dict())

def year(request, year):
    return date_based.archive_year(request, year=year, make_object_list=True, **setup_dict())

def article(request, year, month, slug):
    months = [ x.lower() for x in calendar.month_name ]
    month_id = months.index(month)
    a = Article.objects.get(created__year=year, created__month=month_id, slug=slug)
    day = a.created.day
    return date_based.object_detail(request, year=year, month=month, day=day,
        slug=slug, month_format='%B', slug_field='slug', **setup_dict())

def index(request):
    return date_based.archive_index(request, **setup_dict())

