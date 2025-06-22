from theatricalia import admin
from reversion.admin import VersionAdmin
from .models import Place, Name


class NameInline(admin.TabularInline):
    model = Name
    extra = 1


class PlaceAdmin(VersionAdmin):
    list_filter = ['town', 'country']
    search_fields = ['name', 'town']
    prepopulated_fields = {
        'slug': ('name', 'town'),
    }
    inlines = [
        NameInline,
    ]


admin.site.register(Place, PlaceAdmin)
