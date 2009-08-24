from django import forms
from models import Play
from people.models import Person
from search.views import search_people

class PlayEditForm(forms.ModelForm):
	authors = forms.CharField(widget=forms.HiddenInput)

	class Meta:
		model = Play
		exclude = ('title', 'slug', 'parent')

class PlayAuthorForm(forms.Form):
	id = forms.CharField(widget=forms.HiddenInput, required=False)
	name = forms.CharField(label="Author", max_length=101, required=False)

	def clean_name(self):
		name = self.cleaned_data['name']
		if not name:
			return None
		people, _ = search_people(name, use_distance=False)
		if len(people) == 0:
			raise forms.ValidationError('This name could not be found. Is it a new person?')
		if len(people) == 1:
			return people[0]
			raise forms.ValidationError('We think you mean \xE2\x80\x9C%s\xE2\x80\x9D. Is that right, or is it a new person?' % people[0])
		raise forms.ValidationError(people)
		return name
