from django.contrib import admin
from reversion.admin import VersionAdmin
from .models import Place, Name, Location


class NameInline(admin.TabularInline):
    model = Name
    extra = 1


class LocationInline(admin.TabularInline):
    model = Location
    extra = 1


class PlaceAdmin(VersionAdmin):
    # list_filter = ['town', 'country']
    search_fields = ['name']
    prepopulated_fields = {
        'slug': ('name',),
    }
    inlines = [
        NameInline,
        LocationInline,
    ]


admin.site.register(Place, PlaceAdmin)
