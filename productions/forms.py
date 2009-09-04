import re
from django import forms
from models import Production, Part, Place, ProductionCompany
from plays.models import Play
from places.models import Place as PlacePlace
from people.models import Person
from fields import PrettyDateField, ApproximateDateFormField
from widgets import PrettyDateInput
from django.forms.formsets import BaseFormSet
from search.views import search_people
from common.templatetags.prettify import prettify
from autocomplete.widgets import ForeignKeySearchInput

class CastCrewNullBooleanSelect(forms.widgets.NullBooleanSelect):
    def __init__(self, attrs=None):
        choices = ((u'1', 'Unknown'), (u'2', 'Cast'), (u'3', 'Crew'))
        super(forms.widgets.NullBooleanSelect, self).__init__(attrs, choices)

# Auto-complete for those with JavaScript

class AutoCompleteMultiValueField(forms.MultiValueField):
    def __init__(self, model, column, *args, **kwargs):
        self.model = model
        self.column = column
        super(AutoCompleteMultiValueField, self).__init__(*args, **kwargs)

    def compress(self, data_list):
        if not data_list:
            return None
        if data_list[0] and not data_list[1]:
            data_list[1] = self.model(**{self.column: data_list[0]})
        return data_list[1]

class ProductionForm(forms.ModelForm):
    #last_modified = forms.DateTimeField(widget=forms.HiddenInput(), required=False)
    play = AutoCompleteMultiValueField(
        Play, 'title',
        required = True,
        error_messages = { 'required': 'You must specify a play.' },
        fields = (forms.CharField(), forms.ModelChoiceField(Play.objects.all())),
        widget = ForeignKeySearchInput(Production.play.field.rel, ('title',))
    )
    company = AutoCompleteMultiValueField(
        ProductionCompany, 'name',
        required = False,
        fields = (forms.CharField(), forms.ModelChoiceField(ProductionCompany.objects.all())),
        widget = ForeignKeySearchInput(Production.company.field.rel, ('name',))
    )
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'cols': 40, 'rows':5}))

    class Meta:
        model = Production
        exclude = ('parts', 'places', 'seen_by')

    def __init__(self, last_modified=None, *args, **kwargs):
#        self.db_last_modified = last_modified
#        kwargs.setdefault('initial', {}).update({ 'last_modified': last_modified })
        super(ProductionForm, self).__init__(*args, **kwargs)

#    def clean(self):
#        super(ProductionForm, self).clean()
#
#        # Not clean_last_modified, as I want it as a generic error
#        last_mod = self.cleaned_data.get('last_modified')
#        if last_mod < self.db_last_modified:
#            raise forms.ValidationError('I am afraid that this production has been edited since you started editing.')
#
#        return self.cleaned_data

    def save(self, **kwargs):
        if not self.cleaned_data['play'].id:
            self.cleaned_data['play'].save()
        if self.cleaned_data['company'] and not self.cleaned_data['company'].id:
            self.cleaned_data['company'].save()
        return super(ProductionForm, self).save(**kwargs)

# All the non-JavaScript drop-down stuff

class ForeignKeySearchInputNoJS(forms.MultiWidget):
    """
    A Widget for NOT displaying ForeignKeys in an autocomplete search input 
    instead in a <select> box.
    """
    #def __init__(self, choices=(), model=None, attrs=None):
    def __init__(self, model=None, attrs=None):
        self.model = model
        #widgets = (forms.Select(choices=choices), forms.TextInput(attrs={'size':40}))
        widgets = (forms.Select, forms.TextInput(attrs={'size':40}))
        super(ForeignKeySearchInputNoJS, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value is None:
            return [ value, '' ]
        return [ value, '' ]

    def format_output(self, list):
        name = self.model.__name__
        name = re.sub('([A-Z])', r' \1', name).lower().strip()
        return ('<br>Or if it&rsquo;s a new %s, enter it here: ' % name).join(list)

class AutoCompleteNoJSMultiValueField(forms.MultiValueField):
    def __init__(self, model, column, fields, *args, **kwargs):
        self.model = model
        self.column = column
        #choices = fields[0].choices
        #widget = ForeignKeySearchInputNoJS(choices=choices, model=model)
        widget = ForeignKeySearchInputNoJS(model=model)
        super(AutoCompleteNoJSMultiValueField, self).__init__(fields, widget=widget, *args, **kwargs)

    def compress(self, data_list):
        if not data_list:
            return None
        if data_list[1]:
            data_list[0] = self.model(**{self.column: data_list[1]})
        return data_list[0]

class ProductionFormNoJS(ProductionForm):
    play = AutoCompleteNoJSMultiValueField(
        Play, 'title',
        required = False, # It is required, but will be spotted in the clean function
        fields = (forms.ModelChoiceField(Play.objects.none()), forms.CharField()),
    )
    company = AutoCompleteNoJSMultiValueField(
        ProductionCompany, 'name',
        required = False,
        fields = (forms.ModelChoiceField(ProductionCompany.objects.none()), forms.CharField()),
    )

    def __init__(self, *args, **kwargs):
        super(ProductionFormNoJS, self).__init__(*args, **kwargs)
        self.fields['play'].fields[0].queryset = Play.objects
        # The above line sets some Select widget that is *not* the one actually printed. I don't understand this yet.
        # But anyway, put the choices in the *right* widget.
        self.fields['play'].widget.widgets[0].choices = self.fields['play'].fields[0].choices
        self.fields['company'].fields[0].queryset = ProductionCompany.objects
        self.fields['company'].widget.widgets[0].choices = self.fields['company'].fields[0].choices

class PlaceForm(forms.ModelForm):
    place = AutoCompleteMultiValueField(
        PlacePlace, 'name',
        required = False, # It is required, but will be spotted in the clean function
        fields = (forms.CharField(), forms.ModelChoiceField(PlacePlace.objects.all())),
        widget = ForeignKeySearchInput(Place.place.field.rel, ('name',))
    )
    start_date = ApproximateDateFormField(required=False, label='It ran here from')
    press_date = PrettyDateField(required=False, label='Press night')
    end_date = ApproximateDateFormField(required=False, label='to')

    class Meta:
        model = Place

    def __init__(self, *args, **kwargs):
        super(PlaceForm, self).__init__(*args, **kwargs)
        self.fields['production'].required = False
        self.fields['production'].widget = forms.HiddenInput()

    def clean_place(self):
        if not self.cleaned_data['place']:
            raise forms.ValidationError('You must specify a place.')
        return self.cleaned_data['place']

    def save(self, **kwargs):
        if not self.cleaned_data['place'].id:
            self.cleaned_data['place'].save()
        return super(PlaceForm, self).save(**kwargs)

class PlaceFormNoJS(PlaceForm):
    place = AutoCompleteNoJSMultiValueField(
        PlacePlace, 'name',
        required = False, # It is required, but will be spotted in the clean function
        fields = (forms.ModelChoiceField(PlacePlace.objects.none()), forms.CharField()),
    )

    def __init__(self, *args, **kwargs):
        super(PlaceFormNoJS, self).__init__(*args, **kwargs)
        self.fields['place'].fields[0].queryset = PlacePlace.objects
        # The above line sets some Select widget that is *not* the one actually printed. I don't understand this yet.
        # But anyway, put the choices in the *right* widget.
        self.fields['place'].widget.widgets[0].choices = self.fields['place'].fields[0].choices

# person is the ext box where someone enters a name, and always will be
# person_choice is the selection of someone from that, or the creation of a new person
class PartForm(forms.ModelForm):
    person = forms.CharField(error_messages = {'required':'You have to specify a person.'})
    person_choice = forms.ChoiceField(label='Person', widget=forms.RadioSelect(), required=False)
    start_date = PrettyDateField(required=False, help_text='if they were only in this production for part of its run')
    end_date = PrettyDateField(required=False)

    class Meta:
        model = Part
        exclude = ('order')

    def __init__(self, editing=True, *args, **kwargs):
        super(PartForm, self).__init__(*args, **kwargs)
        self.fields['cast'].widget = CastCrewNullBooleanSelect()
        if not editing:
            self.fields['production'].required = False
        self.fields['production'].widget = forms.HiddenInput()
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

