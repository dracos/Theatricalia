from django.contrib import admin
from reversion.admin import VersionAdmin
from models import Place

class PlaceAdmin(VersionAdmin):
    prepopulated_fields = {
        'slug': ('name',),
    }

admin.site.register(Place, PlaceAdmin)
