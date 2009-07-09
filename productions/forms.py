from django import forms
from models import Production, Part
from fields import PrettyDateField
from django.forms.formsets import BaseFormSet

class CastCrewNullBooleanSelect(forms.widgets.NullBooleanSelect):
    def __init__(self, attrs=None):
        choices = ((u'1', 'Unknown'), (u'2', 'Cast'), (u'3', 'Crew'))
        super(forms.widgets.NullBooleanSelect, self).__init__(attrs, choices)

class ProductionEditForm(forms.ModelForm):
	last_modified = forms.DateTimeField(widget=forms.HiddenInput())
	press_date = PrettyDateField()

	class Meta:
		model = Production
		exclude = ('parts', 'created_by')

	def __init__(self, last_modified=None, *args, **kwargs):
		self.db_last_modified = last_modified
		kwargs['initial'] = { 'last_modified': last_modified }
		super(ProductionEditForm, self).__init__(*args, **kwargs)

#	def clean(self):
#		super(PersonEditForm, self).clean()
#
#		# Not clean_last_modified, as I want it as a generic error
#		last_mod = self.cleaned_data.get('last_modified')
#		if last_mod < self.db_last_modified:
#			raise forms.ValidationError('I am afraid that this person has been edited since you started editing.')
#
#		dob = self.cleaned_data.get('dob')
#		bio = self.cleaned_data.get('bio')
#		imdb = self.cleaned_data.get('imdb')
#		wikipedia = self.cleaned_data.get('wikipedia')
#		web = self.cleaned_data.get('web')
#		if not dob and not bio and not imdb and not wikipedia and not web:
#			raise forms.ValidationError('Please specify at least one item of data')
#		return self.cleaned_data
#
#	def save_with_log(self, request):
#		new_object = self.save(commit=True)

class PartAddForm(forms.ModelForm):
	person = forms.CharField()
	class Meta:
		model = Part
		exclude = ('production', 'credit')
	def __init__(self, *args, **kwargs):
		super(PartAddForm, self).__init__(*args, **kwargs)
		self.fields['order'].widget.attrs['size'] = 5
		self.fields['start_date'].widget.attrs['size'] = 10
		self.fields['end_date'].widget.attrs['size'] = 10
		self.fields['cast'].widget = CastCrewNullBooleanSelect()

class PartEditForm(PartAddForm):
	id = forms.IntegerField(widget=forms.HiddenInput())
	last_modified = forms.DateTimeField(widget=forms.HiddenInput())

	def __init__(self, last_modified=None, *args, **kwargs):
		self.db_last_modified = last_modified
		kwargs.setdefault('initial', {}).update({'last_modified':last_modified})
		super(PartEditForm, self).__init__(*args, **kwargs)

	def clean(self):
		#print "Clean Hello"
		#print self.cleaned_data
		return self.cleaned_data

	def clean_person(self):
		pass #print "Hello"

class BasePartFormSet(BaseFormSet):
	def add_fields(self, form, index):
		super(BasePartFormSet, self).add_fields(form, index)
		form.fields['edit_status'] = forms.ChoiceField(choices=(('leave','Leave'), ('change','Change'), ('remove','Remove')))

	def get_deleted_forms(self):
		self._deleted_form_indexes = []
		for i in range(0, self._total_form_count):
			form = self.forms[i]
			if form.cleaned_data[DELETION_FIELD_NAME]:
				self._deleted_form_indexes.append(i)
		return [self.forms[i] for i in self._deleted_form_indexes]

