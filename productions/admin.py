from django.contrib import admin
from django import forms
from reversion.admin import VersionAdmin
from models import Production, ProductionCompany, Part, Place
from forms import AutoCompleteMultiValueField
from plays.models import Play
from autocomplete.widgets import AutocompleteModelAdmin, ForeignKeySearchInput

class CompanyAdmin(VersionAdmin):
    prepopulated_fields = {
        'slug': ('name',),
    }

class PartAdmin(VersionAdmin, AutocompleteModelAdmin):
    related_search_fields = {
        'production': ('play__title', 'company__name'),
        'person': ('first_name','last_name'),
    }

class PartInlineForm(forms.ModelForm):
    lookup_person = forms.CharField(label='LookupPerson')
    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            kwargs.setdefault('initial', {})['lookup_person'] = kwargs['instance'].person.name()
        super(PartInlineForm, self).__init__(*args, **kwargs)
        self.fields['person'].widget = forms.HiddenInput()

class PartInline(admin.options.InlineModelAdmin):
    template = 'admin/edit_part_inline.html' # To have auto-complete for the inline Part
    model = Part
    form = PartInlineForm
    extra = 1

class ProductionForm(forms.ModelForm):
    play = AutoCompleteMultiValueField(
            Play, 'title',
            fields = (forms.CharField(), forms.ModelChoiceField(Play.objects.all())),
            widget = ForeignKeySearchInput(Production.play.field.rel, ('title',))
    )

    class Meta:
        model = Production
        #exclude = ('parts', 'places', 'seen_by', 'source')

class ProductionAdmin(VersionAdmin, AutocompleteModelAdmin):
    form = ProductionForm
    related_search_fields = {
        #'places': ('name',),
        'play': ('title',),
    }
    inlines = [
        PartInline,
    ]

class PlaceAdmin(VersionAdmin):
    pass

admin.site.register(Production, ProductionAdmin)
admin.site.register(ProductionCompany, CompanyAdmin)
admin.site.register(Part, PartAdmin)
admin.site.register(Place, PlaceAdmin)

