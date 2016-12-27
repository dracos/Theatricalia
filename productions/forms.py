import re, sys
from django import forms
from django.utils.safestring import mark_safe
from django.forms.formsets import BaseFormSet
from django.db.models import Q

from models import Production, Part, Place, ProductionCompany, Production_Companies
from plays.models import Play
from places.models import Place as PlacePlace
from people.models import Person
from fields import PrettyDateField, ApproximateDateFormField, StripCharField
from widgets import PrettyDateInput
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
        required = False, # It is required, but will be spotted in the clean function
        fields = (StripCharField(), forms.ModelChoiceField(Play.objects.all())),
        widget = ForeignKeySearchInput(Production.play.field.rel, ('title',))
    )
    play_choice = forms.ChoiceField(label='Play', widget=forms.RadioSelect(), required=False)
    description = StripCharField(required=False, widget=forms.Textarea(attrs={'cols': 40, 'rows':5}))
    url = forms.URLField(label='Web page', required=False, widget=forms.TextInput(attrs={'size': 40}))
    book_tickets = forms.URLField(label='Booking URL', required=False, widget=forms.TextInput(attrs={'size': 40}))

    def _get_validation_exclusions(self):
        exclusions = super(ProductionForm, self)._get_validation_exclusions()
        exclusions.append('play')
        return exclusions

    class Meta:
        model = Production
        exclude = ('parts', 'places', 'seen_by', 'source', 'companies')

    def __init__(self, last_modified=None, *args, **kwargs):
        super(ProductionForm, self).__init__(*args, **kwargs)
        if 'play_choice' in self.data and 'play_0' in self.data:
            choices = self.play_radio_choices(self.data['play_0'])
            self.fields['play_choice'].choices = choices

    def clean(self):
        if isinstance(self.cleaned_data.get('play_choice'), Play):
            self.cleaned_data['play'] = self.cleaned_data['play_choice']
            del self.cleaned_data['play_choice']
        return self.cleaned_data

    def play_radio_choices(self, s):
        choices = []
        p = ''

        # For database order of articles
        m = re.match('^(A|An|The) (.*)$(?i)', s)
        if m:
            article, rest = m.groups()
            q = Q(title__iendswith=' %s' % article, title__istartswith=rest)
        else:
            q = Q(title__icontains=s)

        for p in Play.objects.filter(q):
            choices.append( ( p.id, prettify(unicode(p)) ) )
        if len(choices) > 1:
            choices.append( ( 'new', prettify('None of these, a new play called \'' + s + '\'') ) )
        elif unicode(p) == s:
            choices.append( ( 'new', prettify('A new play also called \'' + s + '\'') ) )
        else:
            choices.append( ( 'new', prettify('A new play called \'' + s + '\'') ) )
        choices.append( ( 'back', 'I misspelled, and will enter a new title below:' ) )
        return choices

    # play_choice is either blank, an ID, 'new' or 'back'
    def clean_play_choice(self):
        play = self.cleaned_data['play_choice']
        if re.match('[0-9]+$', play):
            return Play.objects.get(id=play)
        if play == 'new' or (play in ('','back') and 'play' in self.cleaned_data and self.cleaned_data['play'].id):
            return play
        raise forms.ValidationError('Please select one of the choices below:')

    # play is either empty, or a Play object (perhaps new, perhaps existing)
    def clean_play(self):
        if not self.cleaned_data['play']:
            raise forms.ValidationError('You must specify a play.')
        play = self.cleaned_data['play']
        if play.id:
            return play
        if not self.fields['play_choice'].choices:
            choices = self.play_radio_choices(play.title)
            self.fields['play_choice'].choices = choices
        return play

    def save(self, **kwargs):
        if not self.cleaned_data['play'].id:
            self.cleaned_data['play'].save()
            # Must reattach the now-saved play to the instance to pass in the ID
            self.instance.play = self.cleaned_data['play']
        return super(ProductionForm, self).save(**kwargs)

class CompanyInlineForm(forms.ModelForm):
    productioncompany = AutoCompleteMultiValueField(
        ProductionCompany, 'name',
        required = False, label='Company',
        fields = (StripCharField(), forms.ModelChoiceField(ProductionCompany.objects.all())),
        widget = ForeignKeySearchInput(Production_Companies.productioncompany.field.rel, ('name',))
    )

    class Meta:
        model = Production_Companies
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(CompanyInlineForm, self).__init__(*args, **kwargs)
        self.fields['production'].required = False
        self.fields['production'].widget = forms.HiddenInput()

    def _get_validation_exclusions(self):
        exclusions = super(CompanyInlineForm, self)._get_validation_exclusions()
        exclusions.append('productioncompany')
        return exclusions

    def save(self, **kwargs):
        if not self.cleaned_data['productioncompany'].id:
            self.cleaned_data['productioncompany'].save()
            # Must reattach the now-saved object to the instance to pass in the ID
            self.instance.productioncompany = self.cleaned_data['productioncompany']
        return super(CompanyInlineForm, self).save(**kwargs)

class PlaceForm(forms.ModelForm):
    place = AutoCompleteMultiValueField(
        PlacePlace, 'name',
        required = False, # It is required, but will be spotted in the clean function
        fields = (StripCharField(), forms.ModelChoiceField(PlacePlace.objects.all())),
        widget = ForeignKeySearchInput(Place.place.field.rel, ('name',))
    )
    start_date = ApproximateDateFormField(required=False, label='It was/is on from')
    press_date = PrettyDateField(required=False, label='Press night')
    end_date = ApproximateDateFormField(required=False, label='to')

    class Meta:
        model = Place
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(PlaceForm, self).__init__(*args, **kwargs)
        self.fields['production'].required = False
        self.fields['production'].widget = forms.HiddenInput()

    def _get_validation_exclusions(self):
        exclusions = super(PlaceForm, self)._get_validation_exclusions()
        exclusions.append('place')
        return exclusions

    def clean_place(self):
        if not self.cleaned_data['place']:
            raise forms.ValidationError('You must specify a place.')
        return self.cleaned_data['place']

    def save(self, **kwargs):
        if not self.cleaned_data['place'].id:
            self.cleaned_data['place'].save(include_town=True)
            # Must reattach the now-saved object to the instance to pass in the ID
            self.instance.place = self.cleaned_data['place']
        return super(PlaceForm, self).save(**kwargs)

# person is the text box where someone enters a name, and always will be
# person_choice is the selection of someone from that, or the creation of a new person
class PartForm(forms.ModelForm):
    person = StripCharField(error_messages = {'required':'You have to specify a person.'})
    person_choice = forms.ChoiceField(label='Person', widget=forms.RadioSelect(), required=False)
    start_date = ApproximateDateFormField(required=False, help_text='if they were only in this production for part of its run')
    end_date = ApproximateDateFormField(required=False)

    _flag_up_no_results = False

    class Meta:
        model = Part
        exclude = ('order',)

    def _get_validation_exclusions(self):
        exclusions = super(PartForm, self)._get_validation_exclusions()
        exclusions.append('person')
        return exclusions

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
            choices.append( (p.id, prettify(mark_safe('<a target="_blank" href="' + p.get_absolute_url() + '">' + unicode(p) + '</a> <small>(new window)</small>, ' + unicode(last))) ) )
        if len(choices) > 1:
            choices.append( ( 'new', prettify('None of these, a new person called \'' + s + '\'') ) )
        elif unicode(p) == s:
            choices.append( ( 'new', prettify('A new person also called \'' + s + '\'') ) )
        else:
            return []
        choices.append( ( 'back', 'I misspelled, and will enter a new name below:' ) )
        return choices

    def clean(self):
        if isinstance(self.cleaned_data.get('person_choice'), Person):
            self.cleaned_data['person'] = self.cleaned_data['person_choice']
            del self.cleaned_data['person_choice']
        return self.cleaned_data

    def clean_person_choice(self):
        person = self.cleaned_data['person_choice']
        if self._flag_up_no_results:
            return 'new'
        if re.match('[0-9]+$', person):
            return Person.objects.get(id=person)
        if person == 'new' or (person == '' and 'person' not in self.changed_data and self.fields['production'].required == True):
            return person
        raise forms.ValidationError('Please select one of the choices below:')

    def clean_person(self):
        if not 'person' in self.changed_data and self.fields['production'].required == True:
            # The person hasn't altered, so use the Person object we already know about
            return self.instance.person

        person = self.cleaned_data['person']
        if not self.fields['person_choice'].choices:
            # Okay, so we have a search string
            choices = self.radio_choices(person)
            if choices:
                self.fields['person_choice'].choices = choices # = forms.ChoiceField( label='Person', choices=choices, widget = forms.RadioSelect() )
            else:
                self._flag_up_no_results = True
        return Person.objects.from_name(person)

    def save(self, **kwargs):
        if self.cleaned_data.get('person_choice') == 'new':
            self.cleaned_data['person'].save()
            # Must reattach the now-saved play to the instance to pass in the ID
            self.instance.person = self.cleaned_data['person']
        return super(PartForm, self).save(**kwargs)

class ProductionCompanyForm(forms.ModelForm):
    class Meta:
        model = ProductionCompany
        exclude = ('slug',)

