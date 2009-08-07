from django.contrib import admin
from reversion.admin import VersionAdmin
from autocomplete.widgets import AutocompleteModelAdmin
from models import Play

class PlayAdmin(VersionAdmin, AutocompleteModelAdmin):
    related_search_fields = {
        'parent': ('title',),
        'authors': ('first_name', 'last_name',),
    }
    prepopulated_fields = {
        'slug': ('title',),
    }

admin.site.register(Play, PlayAdmin)
