from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.forms.models import inlineformset_factory
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django.contrib import messages
from django.shortcuts import render

from mixins import ListMixin

# from common.models import Alert
from .forms import PlaceForm, NameForm
from .models import Place, Name
from shortcuts import check_url, UnmatchingSlugException
from productions.objshow import productions_list, productions_for
from productions.models import Production, Part
from people.models import Person
from photos.forms import PhotoForm


def place_short_url(request, place_id):
    try:
        place = check_url(Place, place_id)
    except UnmatchingSlugException as e:
        place = e.args[0]
    return HttpResponsePermanentRedirect(place.get_absolute_url())


def place_productions(request, place_id, place, type):
    try:
        place = check_url(Place, place_id, place)
    except UnmatchingSlugException as e:
        return HttpResponsePermanentRedirect(e.args[0].get_absolute_url())
    return productions_list(request, place, type, 'places/production_list.html')


def productions(request, place_id, place):
    try:
        place = check_url(Place, place_id, place)
    except UnmatchingSlugException as e:
        return HttpResponsePermanentRedirect(e.args[0].get_absolute_url())

    productions = Production.objects.filter(places=place).order_by('play__title').select_related('play')
    Production.objects.prefetch_companies(productions)
    Production.objects.prefetch_places(productions)

    return render(request, 'places/productions.html', {
        'productions': productions,
        'place': place,
    })


def people(request, place_id, place):
    try:
        place = check_url(Place, place_id, place)
    except UnmatchingSlugException as e:
        return HttpResponsePermanentRedirect(e.args[0].get_absolute_url())

    people = Person.objects.filter(productions__places=place).distinct().order_by('last_name', 'first_name')
    productionsM2M = Part.objects.filter(production__places=place, person__in=people).select_related('production')
    m2m = {}
    for p in productionsM2M:
        m2m.setdefault(p.person_id, []).append(p.production)
    for p in people:
        p._productions = m2m.get(p.id, [])

    return render(request, 'places/people.html', {
        'people': people,
        'place': place,
    })


@login_required
def place_edit(request, place_id, place):
    try:
        place = check_url(Place, place_id, place)
    except UnmatchingSlugException as e:
        return HttpResponsePermanentRedirect(e.args[0].get_absolute_url())

    place.name = place.get_name_display()

    form = PlaceForm(request.POST or None, instance=place)

    NameFormSet = inlineformset_factory(Place, Name, extra=1, form=NameForm)
    name_formset = NameFormSet(
        data=request.POST or None,
        prefix='name',
        instance=place,
    )

    if request.method == 'POST':
        if request.POST.get('disregard'):
            messages.success(request, u"All right, we\u2019ve ignored any changes you made.")
            return HttpResponseRedirect(place.get_absolute_url())
        if form.is_valid() and name_formset.is_valid():
            form.save()
            name_formset.save()
            messages.success(request, "Your changes have been stored; thank you.")
            return HttpResponseRedirect(place.get_absolute_url())

    return render(request, 'places/place_edit.html', {
        'place': place,
        'form': form,
        'name_formset': name_formset,
    })


def place(request, place_id, place):
    try:
        place = check_url(Place, place_id, place)
    except UnmatchingSlugException as e:
        return HttpResponsePermanentRedirect(e.args[0].get_absolute_url())
    past, future = productions_for(place)
    photo_form = PhotoForm(place)
    alert = place.alerts.filter(user=request.user.pk)
    return render(request, 'place.html', {
        'place': place,
        'past': past,
        'future': future,
        'photo_form': photo_form,
        'alert': alert,
    })


# @login_required
# def place_alert(request, place_id, place, type):
#    try:
#        place = check_url(Place, place_id, place)
#    except UnmatchingSlugException as e:
#        return HttpResponsePermanentRedirect(e.args[0].get_absolute_url())
#
#    if type == 'add':
#        alert = Alert(user=request.user, content_object=place)
#        try:
#            alert.save()
#        except IntegrityError as e:
#            if e.args[0] != 1062: # Duplicate
#                raise
#        messages.success(request, u"Your alert has been added.")
#    elif type == 'remove':
#        place.alerts.filter(user=request.user).delete()
#        messages.success(request, u"Your alert has been removed.")
#
#    return HttpResponseRedirect(place.get_absolute_url())


class PlaceList(ListMixin, ListView):
    model = Place
    field = 'name'
    template_name = 'places/place_list.html'

    def get_queryset(self):
        letter = self.kwargs.get('letter', 'a')
        if letter == '0':
            args = {'%s__regex' % self.field: r'^[0-9]'}
            objs1 = Place.objects.filter(**args)
            objs2 = Name.objects.filter(**args)
            letter = '0-9'
        elif letter == '*':
            args = {'%s__regex' % self.field: r'^[A-Za-z0-9]'}
            objs1 = Place.objects.exclude(**args)
            objs2 = Name.objects.exclude(**args)
            letter = 'Symbols'
        else:
            args = {'%s__istartswith' % self.field: letter}
            objs1 = Place.objects.filter(**args)
            objs2 = Name.objects.filter(**args)
            letter = letter.upper()
        self.letter = letter
        objs = list(objs1) + list(objs2)
        return objs
