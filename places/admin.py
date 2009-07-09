from django.contrib import admin
from models import Place

class PlaceAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('name',),
    }

admin.site.register(Place, PlaceAdmin)
