import string
from django.views.generic.list_detail import object_list
from django.forms.formsets import formset_factory
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from shortcuts import render
from models import Play, first_letters
from forms import PlayEditForm, PlayAuthorForm
from datetime import datetime
from productions.views import production_list, object_productions

def play_productions(request, play, type):
	play = get_object_or_404(Play, slug=play)
	return production_list(request, play, type, 'plays/production_list.html')

def play(request, play):
	play = get_object_or_404(Play, slug=play)
	past, future = object_productions(play)
	return render(request, 'plays/play.html', {
		'play': play,
		'past': past,
		'future': future,
	})

@login_required
def play_edit(request, play):
	play = get_object_or_404(Play, slug=play)

	form = PlayEditForm(request.POST or None, instance=play)
	PlayAuthorFormSet = formset_factory(PlayAuthorForm)
	initial = [ { 'id': author.id, 'name': author.name() } for author in play.authors.all() ]
	formset = PlayAuthorFormSet(request.POST or None, initial=initial)
	if request.method == 'POST' and form.is_valid() and formset.is_valid():
		authors = []
		for author in formset.cleaned_data:
			if author and author['name']:
				authors.append(author['name'])
		print "*", authors
		form.cleaned_data['authors'] = authors
		form.save()
		return HttpResponseRedirect(play.get_absolute_url())

	return render(request, 'plays/play_edit.html', {
		'play': play,
		'form': form,
		'formset': formset,
	})


def list(request, letter='a'):
	if letter == '0':
		plays = Play.objects.filter(title__regex=r'^[0-9]')
		letter = '0-9'
	elif letter == '*':
		plays = Play.objects.exclude(title__regex=r'^[A-Za-z0-9]')
		letter = 'Symbols'
	else:
		plays = Play.objects.filter(title__istartswith=letter)
		letter = letter.upper()
	letters = [ x[0] for x in first_letters() if x[0]>='A' and x[0]<='Z' ]
	letters.sort()
	return object_list(request, queryset=plays, extra_context={ 'letter': letter, 'letters': letters })

