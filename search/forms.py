from django import forms
from fields import ApproximateDateFormField

class SearchForm(forms.Form):
    play = forms.CharField()
    person = forms.CharField()
    place = forms.CharField()
    #date = ApproximateDateFormField()
    #role = forms.CharField()

