from django.contrib import admin
from reversion.admin import VersionAdmin
from models import Place

class PlaceAdmin(VersionAdmin):
    list_filter = ['town','country']
    search_fields = ['name', 'town']
    prepopulated_fields = {
        'slug': ('name',),
    }

admin.site.register(Place, PlaceAdmin)
