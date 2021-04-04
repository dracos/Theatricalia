from django import forms
from .models import Place
from productions.forms import AutoCompleteMultiValueField
from autocomplete.widgets import ForeignKeySearchInput


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
