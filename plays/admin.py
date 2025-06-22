from theatricalia import admin
from reversion.admin import VersionAdmin
from autocomplete.widgets import AutocompleteModelAdmin
from .models import Play


class PlayAdmin(VersionAdmin, AutocompleteModelAdmin):
    related_search_fields = {
        'parent': ('title',),
        'authors': ('first_name', 'last_name',),
    }
    prepopulated_fields = {
        'slug': ('title',),
    }
    search_fields = ['title', 'authors__first_name', 'authors__last_name']


admin.site.register(Play, PlayAdmin)
