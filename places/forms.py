from django import forms
from models import Place
from fields import PrettyDateField

class PlaceForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'cols': 30, 'rows':5}), required=False)
    opening_date = PrettyDateField(required=False)
    class Meta:
        model = Place
        exclude = ('slug',)

