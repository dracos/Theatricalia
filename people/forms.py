from django import forms
from models import Person
from admin import PersonAdmin

class PersonEditForm(forms.ModelForm):
	last_modified = forms.DateTimeField(widget=forms.HiddenInput(), required=False)

	class Meta:
		model = Person
		exclude = ('first_name', 'last_name', 'slug')

	def __init__(self, last_modified=None, *args, **kwargs):
		self.db_last_modified = last_modified
		kwargs['initial'] = { 'last_modified': last_modified }
		super(PersonEditForm, self).__init__(*args, **kwargs)

	def clean(self):
		super(PersonEditForm, self).clean()

		# Not clean_last_modified, as I want it as a generic error
		last_mod = self.cleaned_data.get('last_modified')
		if last_mod < self.db_last_modified:
			raise forms.ValidationError('I am afraid that this person has been edited since you started editing.')

		dob = self.cleaned_data.get('dob')
		bio = self.cleaned_data.get('bio')
		imdb = self.cleaned_data.get('imdb')
		wikipedia = self.cleaned_data.get('wikipedia')
		web = self.cleaned_data.get('web')
		if not dob and not bio and not imdb and not wikipedia and not web:
			raise forms.ValidationError('Please specify at least one item of data')
		return self.cleaned_data

	def save_with_log(self, request):
		new_object = self.save(commit=True)
		# Yucky hook into the admin logging system
		admin = PersonAdmin(Person, None)
		change_message = admin.construct_change_message(request, self, None)
		admin.log_change(request, new_object, change_message)
