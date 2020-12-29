import re
from django import forms
from django.utils.safestring import mark_safe
from .models import Play
from people.models import Person
from search.views import search_people
from common.templatetags.prettify import prettify


class PlayEditForm(forms.ModelForm):
    authors = forms.CharField(widget=forms.HiddenInput)
    # description = forms.CharField(widget=forms.Textarea(attrs={'cols':50, 'rows':10}))

    class Meta:
        model = Play
        exclude = ('slug', 'parent')


class PlayAuthorForm(forms.Form):
    person = forms.CharField(label='Author', max_length=101, required=False)
    person_choice = forms.ChoiceField(label='Author', widget=forms.RadioSelect(), required=False)

    def __init__(self, *args, **kwargs):
        super(PlayAuthorForm, self).__init__(*args, **kwargs)
        # Submitting the form with something selected in person_choice...
        if 'person_choice' in self.data and 'person' in self.data:
            choices = self.radio_choices(self.data['person'])
            self.fields['person_choice'].choices = choices

    def radio_choices(self, s):
        people, dummy = search_people(s, use_distance=False)
        choices = []
        p = ''
        for p in people:
            last_production = p.productions.extra(select={'best_date': 'IFNULL(productions_place.press_date, IF(productions_place.end_date!="", productions_place.end_date, productions_place.start_date))'}).order_by('-best_date', 'place__press_date')[:1]
            if len(last_production):
                part = last_production[0].part_set.filter(person=p)[:1]
                if len(part):
                    part = part[0].role
                else:
                    part = 'unknown'
                last = u'last in %s as %s' % (last_production[0], part)
            else:
                last_play = p.plays.order_by('-id')[:1]
                if len(last_play):
                    last = 'author of %s' % last_play[0].get_title_display()
                else:
                    last = 'nothing yet on this site'
            choices.append((p.id, prettify(mark_safe('<a target="_blank" href="' + p.get_absolute_url() + '">' + str(p) + '</a> <small>(new window)</small>, ' + str(last)))))
        if len(choices) > 1:
            choices.append(('new', prettify('None of these, a new person called \'' + s + '\'')))
        elif str(p) == s:
            choices.append(('new', prettify('A new person also called \'' + s + '\'')))
        else:
            choices.append(('new', prettify('A new person called \'' + s + '\'')))
        choices.append(('back', 'I misspelled, and will enter a new name below:'))
        return choices

    def clean(self):
        if isinstance(self.cleaned_data.get('person_choice'), Person):
            self.cleaned_data['person'] = self.cleaned_data['person_choice']
            del self.cleaned_data['person_choice']
        return self.cleaned_data

    def clean_person_choice(self):
        person_choice = self.cleaned_data['person_choice']
        if re.match('[0-9]+$', person_choice):
            return Person.objects.get(id=person_choice)
        if person_choice == 'new' or (person_choice == '' and 'person' not in self.changed_data) or (person_choice == '' and 'person' in self.changed_data and self.cleaned_data['person'] == ''):
            return person_choice
        raise forms.ValidationError('Please select one of the choices below:')

    def clean_person(self):
        if 'person' not in self.changed_data:
            # The person hasn't altered, so use the Person object we already know about
            return self.initial['person']

        person = self.cleaned_data['person']
        if not self.fields['person_choice'].choices and person:
            # Okay, so we have a search string
            choices = self.radio_choices(person)
            self.fields['person_choice'].choices = choices  # = forms.ChoiceField( label='Person', choices=choices, widget = forms.RadioSelect() )
        return person
