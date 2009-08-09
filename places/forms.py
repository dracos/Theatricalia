from django import forms
from models import Place
from widgets import LocationWidget

class PlaceForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'cols': 30, 'rows':5}), required=False)
    latitude = forms.FloatField(widget=LocationWidget, label='Location', required=False)
    longitude = forms.FloatField(widget=forms.widgets.HiddenInput, required=False)
    class Meta:
        model = Place
        exclude = ('slug',)

