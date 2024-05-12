from django import forms
from .models import Place, Name
from productions.forms import AutoCompleteMultiValueField
from autocomplete.widgets import ForeignKeySearchInput
from fields import ApproximateDateFormField


class PlaceForm(forms.ModelForm):
    parent = AutoCompleteMultiValueField(
        Place, 'name',
        required=False,
        fields=(forms.CharField(max_length=100), forms.ModelChoiceField(Place.objects.all())),
        widget=ForeignKeySearchInput(
            Place.parent.field.remote_field, ('name', 'parent__name'),
            {'max_length': 100})
    )

    class Meta:
        model = Place
        exclude = ('slug',)

    def __init__(self, *args, **kwargs):
        super(PlaceForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs = {'size': 40}
        self.fields['description'].widget.attrs = {'cols': 40, 'rows': 5}
        self.fields['closing_date'].help_text = \
            'The opening and closing dates may simply be month and year, or just year, if that is all that is known.'

    def clean(self):
        cleaned_data = super().clean()
        if 'parent' in cleaned_data and cleaned_data['parent'] and not cleaned_data['parent'].id:
            cleaned_data['parent'] = None


class NameForm(forms.ModelForm):
    start_date = ApproximateDateFormField(required=False, label='Called this from')
    end_date = ApproximateDateFormField(required=False, label='to')

    class Meta:
        model = Name
        fields = "__all__"
