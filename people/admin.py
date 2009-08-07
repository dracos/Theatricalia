from django.contrib import admin
from reversion.admin import VersionAdmin
from models import Person

class PersonAdmin(VersionAdmin):
	prepopulated_fields = { 'slug': ( 'first_name', 'last_name' ) }

admin.site.register(Person, PersonAdmin)

