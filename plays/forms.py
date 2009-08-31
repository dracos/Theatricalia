import re
from django import forms
from models import Play
from people.models import Person
from search.views import search_people
from common.templatetags.prettify import prettify

class PlayEditForm(forms.ModelForm):
	authors = forms.CharField(widget=forms.HiddenInput)

	class Meta:
		model = Play
		exclude = ('title', 'slug', 'parent')

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
            last_production = p.productions.order_by('-IFNULL(productions_place.press_date, IF(productions_place.end_date!="", productions_place.end_date, productions_place.start_date))', 'place__press_date')
            if len(last_production):
                last_production = last_production[0]
            else:
                last_production = 'nothing yet on this site'
            choices.append( (p.id, prettify(str(p) + ', last in ' + str(last_production)) ) )
        if len(choices) > 1:
            choices.append( ( 'new', prettify('None of these, a new person called \'' + s + '\'') ) )
        elif str(p) == s:
            choices.append( ( 'new', prettify('A new person also called \'' + s + '\'') ) )
        else:
            choices.append( ( 'new', prettify('A new person called \'' + s + '\'') ) )
        choices.append( ( 'back', 'I misspelled, and will enter a new name below:' ) )
        return choices

    def clean(self):
        if isinstance(self.cleaned_data.get('person_choice'), Person):
            self.cleaned_data['person'] = self.cleaned_data['person_choice']
            del self.cleaned_data['person_choice']
        return self.cleaned_data

    def clean_person_choice(self):
        person = self.cleaned_data['person_choice']
        if re.match('[0-9]+$', person):
            return Person.objects.get(id=person)
        if person == 'new' or person == '':
            return person
        raise forms.ValidationError('Please select one of the choices below:')

    def clean_person(self):
        if not 'person' in self.changed_data:
            # The person hasn't altered, so use the Person object we already know about
            return self.initial['person']

        person = self.cleaned_data['person']
        if not self.fields['person_choice'].choices:
            # Okay, so we have a search string
            choices = self.radio_choices(person)
            self.fields['person_choice'].choices = choices # = forms.ChoiceField( label='Person', choices=choices, widget = forms.RadioSelect() )
        return person


