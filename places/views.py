import string
from datetime import datetime

from django.views.generic.list_detail import object_list
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from forms import PlaceForm
from models import Place, first_letters
from shortcuts import render, check_url, UnmatchingSlugException
from productions.views import production_list, object_productions
from photos.forms import PhotoForm

def place_productions(request, place_id, place, type):
    place = check_url(Place, place_id, place)
    return production_list(request, place, type, 'places/production_list.html')

@login_required
def place_edit(request, place_id, place):
    place = check_url(Place, place_id, place)

    form = PlaceForm(request.POST or None, instance=place)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return HttpResponseRedirect(place.get_absolute_url())

    return render(request, 'places/place_edit.html', {
        'place': place,
        'form': form,
    })

def place(request, place_id, place):
    try:
        place = check_url(Place, place_id, place)
    except UnmatchingSlugException, e:
        return HttpResponseRedirect(e.args[0].get_absolute_url())
    past, future = object_productions(place)
    photo_form = PhotoForm(place)
    return render(request, 'place.html', {
        'place': place,
        'past': past,
        'future': future,
        'photo_form': photo_form,
    })

def list(request, letter='a'):
    if letter == '0':
        places = Place.objects.filter(name__regex=r'^[0-9]')
        letter = '0-9'
    elif letter == '*':
        places = Place.objects.exclude(name__regex=r'^[A-Za-z0-9]')
        letter = 'Symbols'
    else:
        places = Place.objects.filter(name__istartswith=letter)
        letter = letter.upper()
    letters = [ x[0] for x in first_letters() ]
    letters.sort()
    return object_list(request, queryset=places, paginate_by=25, extra_context={ 'letter': letter, 'letters': letters })

