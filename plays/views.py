import string
from datetime import datetime
from django.views.generic import ListView
from django.forms.formsets import formset_factory
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect 
from django.db.models import Q
from django.views.decorators.cache import cache_page
from django.contrib import messages
from django.shortcuts import render

from mixins import ListMixin

from shortcuts import check_url, UnmatchingSlugException
from .models import Play
from people.models import Person
from .forms import PlayEditForm, PlayAuthorForm
from productions.objshow import productions_list, productions_for
from common.models import Alert

def play_short_url(request, play_id):
    try:
        play = check_url(Play, play_id)
    except UnmatchingSlugException as e:
        play = e.args[0]
    return HttpResponsePermanentRedirect(play.get_absolute_url())

def play_productions(request, play_id, play, type):
    try:
        play = check_url(Play, play_id, play)
    except UnmatchingSlugException as e:
        if type == 'future':
            url = e.args[0].get_future_url()
        elif type == 'past':
            url = e.args[0].get_past_url()
        return HttpResponsePermanentRedirect(url)
    return productions_list(request, play, type, 'plays/production_list.html')

def play(request, play_id, play):
    try:
        play = check_url(Play, play_id, play)
    except UnmatchingSlugException as e:
        return HttpResponsePermanentRedirect(e.args[0].get_absolute_url())
    past, future = productions_for(play)
    alert = play.alerts.filter(user=request.user.pk)
    same_name = Play.objects.filter(title=play.title).exclude(id=play.id)
    return render(request, 'plays/play.html', {
        'play': play,
        'past': past,
        'future': future,
        'alert': alert,
        'same_name': same_name,
    })

#@login_required
#def play_alert(request, play_id, play, type):
#    try:
#        play = check_url(Play, play_id, play)
#    except UnmatchingSlugException as e:
#        return HttpResponsePermanentRedirect(e.args[0].get_absolute_url())
#
#    if type == 'add':
#        alert = Alert(user=request.user, content_object=play)
#        try:
#            alert.save()
#        except IntegrityError as e:
#            if e.args[0] != 1062: # Duplicate
#                raise
#        messages.success(request, u"Your alert has been added.")
#    elif type == 'remove':
#        play.alerts.filter(user=request.user).delete()
#        messages.success(request, u"Your alert has been removed.")
#
#    return HttpResponseRedirect(play.get_absolute_url())

@login_required
def play_edit(request, play_id, play):
    try:
        play = check_url(Play, play_id, play)
    except UnmatchingSlugException as e:
        return HttpResponsePermanentRedirect(e.args[0].get_edit_url())

    play.title = play.get_title_display()
    form = PlayEditForm(request.POST or None, instance=play)
    PlayAuthorFormSet = formset_factory(PlayAuthorForm)
    initial = [ { 'person': author.name() } for author in play.authors.all() ]
    formset = PlayAuthorFormSet(request.POST or None, initial=initial)
    if request.method == 'POST':
        if request.POST.get('disregard'):
            messages.success(request, u"All right, we\u2019ve ignored any changes you made.")
            return HttpResponseRedirect(play.get_absolute_url())
        if form.is_valid() and formset.is_valid():
            authors = []
            name_to_id = { author.name():author for author in play.authors.all() }
            for author in formset.cleaned_data:
                if author and author['person']:
                    if author.get('person_choice') == 'new':
                        author['person'] = Person.objects.create_from_name(author['person'])
                    elif author.get('person_choice') == '':
                        author['person'] = name_to_id[author['person']]
                    authors.append(author['person'])
            form.cleaned_data['authors'] = authors
            form.save()
            messages.success(request, "Your changes have been stored; thank you.")
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
