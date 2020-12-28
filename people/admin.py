from django.contrib import admin
from reversion.admin import VersionAdmin
from .models import Person

class PersonAdmin(VersionAdmin):
    search_fields = ['first_name', 'last_name']
    prepopulated_fields = { 'slug': ( 'first_name', 'last_name' ) }

admin.site.register(Person, PersonAdmin)

