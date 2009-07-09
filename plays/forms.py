from django import forms
from models import Play
from people.models import Person
from search.views import search_people

class PlayEditForm(forms.ModelForm):
	authors = forms.CharField(widget=forms.HiddenInput)

	class Meta:
		model = Play
		exclude = ('title', 'slug', 'parent', 'created_by')

	#def clean(self):
	#	super(PersonEditForm, self).clean()
		#dob = self.cleaned_data.get('dob')
		#bio = self.cleaned_data.get('bio')
		#imdb = self.cleaned_data.get('imdb')
		#wikipedia = self.cleaned_data.get('wikipedia')
		#web = self.cleaned_data.get('web')
		#if not dob and not bio and not imdb and not wikipedia and not web:
		#	raise ValidationError('Please specify at least one item of data')
	#	return self.cleaned_data

class PlayAuthorForm(forms.Form):
	id = forms.CharField(widget=forms.HiddenInput, required=False)
	name = forms.CharField(label="Author", max_length=101, required=False)

	def clean_name(self):
		name = self.cleaned_data['name']
		if not name:
			return None
		people, _ = search_people(name)
		print people
		if len(people) == 0:
			raise forms.ValidationError('This name could not be found. Is it a new person?')
		if len(people) == 1:
			return people[0]
			raise forms.ValidationError('We think you mean \xE2\x80\x9C%s\xE2\x80\x9D. Is that right, or is it a new person?' % people[0])
		raise forms.ValidationError(people)
		return name
