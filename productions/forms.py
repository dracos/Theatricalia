import re
from django import forms
from models import Production, Part, Place
from people.models import Person
from fields import PrettyDateField, ApproximateDateFormField
from widgets import PrettyDateInput
from django.forms.formsets import BaseFormSet
from search.views import search_people
from common.templatetags.prettify import prettify

class CastCrewNullBooleanSelect(forms.widgets.NullBooleanSelect):
    def __init__(self, attrs=None):
        choices = ((u'1', 'Unknown'), (u'2', 'Cast'), (u'3', 'Crew'))
        super(forms.widgets.NullBooleanSelect, self).__init__(attrs, choices)

class ProductionForm(forms.ModelForm):
    #last_modified = forms.DateTimeField(widget=forms.HiddenInput(), required=False)
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'cols': 40, 'rows':5}))

    class Meta:
        model = Production
        exclude = ('parts', 'places')

#    def __init__(self, last_modified=None, *args, **kwargs):
#        self.db_last_modified = last_modified
#        kwargs.setdefault('initial', {}).update({ 'last_modified': last_modified })
#        super(ProductionForm, self).__init__(*args, **kwargs)
#
#    def clean(self):
#        super(ProductionForm, self).clean()
#
#        # Not clean_last_modified, as I want it as a generic error
#        last_mod = self.cleaned_data.get('last_modified')
#        if last_mod < self.db_last_modified:
#            raise forms.ValidationError('I am afraid that this production has been edited since you started editing.')
#
#        return self.cleaned_data

class PlaceForm(forms.ModelForm):
    # All this just to shrink them a bit
    start_date = ApproximateDateFormField(required=False, label='It ran here from')
    press_date = PrettyDateField(required=False, label='Press night')
    end_date = ApproximateDateFormField(required=False, label='to')
    class Meta:
        model = Place

# person is the ext box where someone enters a name, and always will be
# person_choice is the selection of someone from that, or the creation of a new person
class PartForm(forms.ModelForm):
    person = forms.CharField()
    person_choice = forms.ChoiceField(label='Person', widget=forms.RadioSelect(), required=False)

    class Meta:
        model = Part
        exclude = ('production', 'order')

    def __init__(self, *args, **kwargs):
        super(PartForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].help_text = 'if they were only in this production for part of its run'
        self.fields['cast'].widget = CastCrewNullBooleanSelect()
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
        if person == 'new' or (person == '' and 'person' not in self.changed_data):
            return person
        raise forms.ValidationError('Please select one of the choices below:')

    def clean_person(self):
        if not 'person' in self.changed_data:
            # The person hasn't altered, so use the Person object we already know about
            return self.instance.person

        person = self.cleaned_data['person']
        if not self.fields['person_choice'].choices:
            # Okay, so we have a search string
            choices = self.radio_choices(person)
            self.fields['person_choice'].choices = choices # = forms.ChoiceField( label='Person', choices=choices, widget = forms.RadioSelect() )
        return person

