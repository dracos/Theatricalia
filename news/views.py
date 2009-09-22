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
    return date_based.object_detail(request, year=year, month=month, day=21,
        slug=slug, month_format='%B', slug_field='slug', **setup_dict())

def index(request):
    return date_based.archive_index(request, **setup_dict())

