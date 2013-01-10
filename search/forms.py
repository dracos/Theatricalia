from django import forms
from fields import ApproximateDateFormField

class SearchForm(forms.Form):
    play = forms.CharField(required=False)
    person = forms.CharField(required=False)
    place = forms.CharField(required=False)
    #date = ApproximateDateFormField()
    #role = forms.CharField()

