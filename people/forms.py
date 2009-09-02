from django import forms
from models import Person
from admin import PersonAdmin

class PersonEditForm(forms.ModelForm):
    #last_modified = forms.DateTimeField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Person
        exclude = ('first_name', 'last_name', 'slug')

    def __init__(self, last_modified=None, *args, **kwargs):
        #self.db_last_modified = last_modified
        #kwargs['initial'] = { 'last_modified': last_modified }
        super(PersonEditForm, self).__init__(*args, **kwargs)
        self.fields['dob'].help_text = 'Date of birth may simply be month and year, or just year, if that is all that is known.'

    def clean(self):
        super(PersonEditForm, self).clean()

        # Not clean_last_modified, as I want it as a generic error
        #last_mod = self.cleaned_data.get('last_modified')
        #if last_mod < self.db_last_modified:
        #    raise forms.ValidationError('I am afraid that this person has been edited since you started editing.')

        dob = self.cleaned_data.get('dob')
        bio = self.cleaned_data.get('bio')
        imdb = self.cleaned_data.get('imdb')
        wikipedia = self.cleaned_data.get('wikipedia')
        web = self.cleaned_data.get('web')
        if not self.errors and not dob and not bio and not imdb and not wikipedia and not web:
            raise forms.ValidationError('Please specify at least one item of data.')
        return self.cleaned_data

