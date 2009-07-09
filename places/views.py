import string
from datetime import datetime
from models import Place, first_letters
from django.views.generic.list_detail import object_list
from django.db.models import Q
from django.shortcuts import get_object_or_404
from shortcuts import render
from productions.views import production_list, object_productions
from photos.forms import PhotoForm

def place_productions(request, place, type):
	place = get_object_or_404(Place, slug=place)
	return production_list(request, place, type, 'places/production_list.html')


def place(request, place):
	place = get_object_or_404(Place, slug=place)
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

