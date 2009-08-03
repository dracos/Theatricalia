import re
from django import forms
from models import Production, Part
from people.models import Person
from fields import PrettyDateField
from django.forms.formsets import BaseFormSet
from search.views import search_people

class CastCrewNullBooleanSelect(forms.widgets.NullBooleanSelect):
    def __init__(self, attrs=None):
        choices = ((u'1', 'Unknown'), (u'2', 'Cast'), (u'3', 'Crew'))
        super(forms.widgets.NullBooleanSelect, self).__init__(attrs, choices)

class ProductionEditForm(forms.ModelForm):
    last_modified = forms.DateTimeField(widget=forms.HiddenInput(), required=False)
    press_date = PrettyDateField()
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'cols': 30, 'rows':5}))

    class Meta:
        model = Production
        exclude = ('parts', 'created_by')

    def __init__(self, last_modified=None, *args, **kwargs):
        self.db_last_modified = last_modified
        kwargs['initial'] = { 'last_modified': last_modified }
        super(ProductionEditForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(ProductionEditForm, self).clean()

        # Not clean_last_modified, as I want it as a generic error
        last_mod = self.cleaned_data.get('last_modified')
        if last_mod < self.db_last_modified:
            raise forms.ValidationError('I am afraid that this production has been edited since you started editing.')

#       bio = self.cleaned_data.get('bio')
#       if not dob and not bio and not imdb and not wikipedia and not web:
#           raise forms.ValidationError('Please specify at least one item of data')
        return self.cleaned_data

class PartAddForm(forms.ModelForm):
    person = forms.CharField()
    class Meta:
        model = Part
        exclude = ('production', 'credit', 'created_by', 'visible')
    def __init__(self, *args, **kwargs):
        super(PartAddForm, self).__init__(*args, **kwargs)
        self.fields['order'].widget.attrs['size'] = 5
        self.fields['start_date'].widget.attrs['size'] = 10
        self.fields['end_date'].widget.attrs['size'] = 10
        self.fields['cast'].widget = CastCrewNullBooleanSelect()

class PartEditForm(PartAddForm):
    id = forms.IntegerField(widget=forms.HiddenInput())
#    last_modified = forms.DateTimeField(widget=forms.HiddenInput())

    def __init__(self, last_modified=None, person_state=None, *args, **kwargs):
#        self.db_last_modified = last_modified
#        kwargs.setdefault('initial', {}).update({'last_modified':last_modified})
        if person_state == 'radio':
            self.fields['person'].widget = forms.RadioSelect()
        super(PartEditForm, self).__init__(*args, **kwargs)

#    def clean(self):
#        if 'edit_status' in self.cleaned_data and self.cleaned_data['edit_status'] == 'leave':
#            del self._errors
#        return self.cleaned_data

    def clean_person(self):
        if not 'person' in self.changed_data:
            # The person hasn't altered, so use the Person object we already know about
            return self.instance.person

        # Okay, so the name doesn't match the database.
        # Firstly, is it because it's a new ID?
        person = self.cleaned_data['person']
        if re.match('[0-9]+$', person):
            return Person.objects.get(id=person)

        # Okay, so we have a search string
        people, dummy = search_people(person)
        choices = []
        for p in people:
            choices.append( (p.id, str(p) ) )
        choices.append( ( 'new', 'None of these, a new person' ) )
        self.fields['person'] = forms.ChoiceField( choices=choices, widget = forms.RadioSelect() )
        raise forms.ValidationError(people)

# The FormSet class for editing parts - coping with string name, not <select> etc.
class BasePartFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(BasePartFormSet, self).__init__(*args, **kwargs)

    def add_fields(self, form, index):
        super(BasePartFormSet, self).add_fields(form, index)
        form.fields['edit_status'] = forms.ChoiceField(choices=(('leave','Leave'), ('change','Change'), ('remove','Remove')))

    def _construct_form(self, i, **kwargs):
        if i < self._initial_form_count:
            kwargs['instance'] = self.initial[i]['part']
        return super(BasePartFormSet, self)._construct_form(i, **kwargs)

    def save(self):
        for form in self.initial_forms:
            if form.changed_data:
                form.save()

    # XXX
    def get_deleted_forms(self):
        self._deleted_form_indexes = []
        for i in range(0, self._total_form_count):
            form = self.forms[i]
            if form.cleaned_data[DELETION_FIELD_NAME]:
                self._deleted_form_indexes.append(i)
        return [self.forms[i] for i in self._deleted_form_indexes]

