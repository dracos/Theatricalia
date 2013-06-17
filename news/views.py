import calendar
from django.views.generic import dates
from models import Article

MONTHS = [ m.lower() for m in calendar.month_name ]

class NewsMixin(object):
    date_field = 'created'

    def get_queryset(self):
        if self.request.user.is_staff == 1:
            qs = Article.objects.all()
        else:
            qs = Article.objects.visible()
        return qs

    def get_context_data(self, **kwargs):
        context = super(NewsMixin, self).get_context_data(**kwargs)
        context['all'] = self.get_queryset()
        return context

class NewsMonth(NewsMixin, dates.MonthArchiveView):
    month_format = '%B'

class NewsYear(NewsMixin, dates.YearArchiveView):
    make_object_list = True

class NewsArticle(NewsMixin, dates.DateDetailView):
    month_format = '%B'

    def get_day(self):
        """"No day in URL, easiest just to fake it from a quick lookup."""
        a = Article.objects.get(**{
            '%s__year' % self.date_field: self.get_year(),
            '%s__month' % self.date_field: MONTHS.index(self.get_month()),
            self.get_slug_field(): self.kwargs.get(self.slug_url_kwarg),
        })
        day = a.created.day
        return str(day)

class NewsIndex(NewsMixin, dates.ArchiveIndexView):
    pass
