from django.contrib import admin
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

class PartInline(admin.options.InlineModelAdmin):
    template = 'edit_inline.html'
    model = Part
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


