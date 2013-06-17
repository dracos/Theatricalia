import string
from datetime import datetime
from django.views.generic import ListView
from django.forms.formsets import formset_factory
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect 
from django.db.models import Q
from django.views.decorators.cache import cache_page

from mixins import ListMixin

from shortcuts import render, check_url, UnmatchingSlugException
from models import Play
from people.models import Person
from forms import PlayEditForm, PlayAuthorForm
from productions.objshow import productions_list, productions_for
from common.models import Alert

def play_short_url(request, play_id):
    try:
        play = check_url(Play, play_id)
    except UnmatchingSlugException, e:
        play = e.args[0]
    return HttpResponsePermanentRedirect(play.get_absolute_url())

def play_productions(request, play_id, play, type):
    try:
        play = check_url(Play, play_id, play)
    except UnmatchingSlugException, e:
        return HttpResponseRedirect(e.args[0].get_absolute_url())
    return productions_list(request, play, type, 'plays/production_list.html')

def play(request, play_id, play):
    try:
        play = check_url(Play, play_id, play)
    except UnmatchingSlugException, e:
        return HttpResponseRedirect(e.args[0].get_absolute_url())
    past, future = productions_for(play)
    alert = play.alerts.filter(user=request.user)
    same_name = Play.objects.filter(title=play.title).exclude(id=play.id)
    return render(request, 'plays/play.html', {
        'play': play,
        'past': past,
        'future': future,
        'alert': alert,
        'same_name': same_name,
    })

@login_required
def play_alert(request, play_id, play, type):
    try:
        play = check_url(Play, play_id, play)
    except UnmatchingSlugException, e:
        return HttpResponseRedirect(e.args[0].get_absolute_url())

    if type == 'add':
        alert = Alert(user=request.user, content_object=play)
        try:
            alert.save()
        except IntegrityError, e:
            if e.args[0] != 1062: # Duplicate
                raise
        request.user.message_set.create(message=u"Your alert has been added.")
    elif type == 'remove':
        play.alerts.filter(user=request.user).delete()
        request.user.message_set.create(message=u"Your alert has been removed.")

    return HttpResponseRedirect(play.get_absolute_url())

@login_required
def play_edit(request, play_id, play):
    try:
        play = check_url(Play, play_id, play)
    except UnmatchingSlugException, e:
        return HttpResponseRedirect(e.args[0].get_absolute_url())

    form = PlayEditForm(request.POST or None, instance=play)
    PlayAuthorFormSet = formset_factory(PlayAuthorForm)
    initial = [ { 'person': author } for author in play.authors.all() ]
    formset = PlayAuthorFormSet(request.POST or None, initial=initial)
    if request.method == 'POST':
        if request.POST.get('disregard'):
            request.user.message_set.create(message=u"All right, we\u2019ve ignored any changes you made.")
            return HttpResponseRedirect(play.get_absolute_url())
        if form.is_valid() and formset.is_valid():
            authors = []
            for author in formset.cleaned_data:
                if author and author['person']:
                    if author.get('person_choice') == 'new':
                        author['person'] = Person.objects.create_from_name(author['person'])
                    authors.append(author['person'])
            form.cleaned_data['authors'] = authors
            form.save()
            request.user.message_set.create(message="Your changes have been stored; thank you.")
            return HttpResponseRedirect(play.get_absolute_url())

    return render(request, 'plays/play_edit.html', {
        'play': play,
        'form': form,
        'formset': formset,
    })

class PlayList(ListMixin, ListView):
    model = Play
    field = 'title'

    def get_queryset(self):
        objs = super(PlayList, self).get_queryset()
        letter = self.kwargs.get('letter', 'a')
        if letter == '0':
            pass
        elif letter == '*':
            args = { '%s__regex' % self.field: r'^(\'|")[A-Za-z]' }
            objs = objs.exclude(**args)
        else:
            plays = self.model.objects.filter( Q(title__istartswith=letter) | Q(title__istartswith="'%s" % letter) | Q(title__istartswith='"%s' % letter) )
            letter = letter.upper()
        return objs
