from django.contrib import admin
from django import forms
from reversion.admin import VersionAdmin
from models import Production, ProductionCompany, Part, Performance
from autocomplete.widgets import AutocompleteModelAdmin

class CompanyAdmin(VersionAdmin):
    prepopulated_fields = {
        'slug': ('name',),
    }

class PartAdmin(VersionAdmin, AutocompleteModelAdmin):
    related_search_fields = {
        'production': ('play__title', 'company__name', 'start_date', 'end_date'),
        'person': ('first_name','last_name'),
    }

class PartInlineForm(forms.ModelForm):
    lookup_person = forms.CharField()
    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            kwargs['initial']['lookup_person'] = kwargs['instance'].person.name()
        super(PartInlineForm, self).__init__(*args, **kwargs)
        self.fields['person'].widget = forms.HiddenInput()

class PartInline(admin.options.InlineModelAdmin):
    template = 'admin/edit_part_inline.html' # To have auto-complete for the inline Part
    model = Part
    form = PartInlineForm
    extra = 1

class ProductionAdmin(VersionAdmin, AutocompleteModelAdmin):
    related_search_fields = {
        'places': ('name',),
        'play': ('title',),
    }
    inlines = [
        PartInline,
    ]

admin.site.register(Production, ProductionAdmin)
admin.site.register(ProductionCompany, CompanyAdmin)
admin.site.register(Part, PartAdmin)
admin.site.register(Performance, VersionAdmin)


