from django.contrib import admin
from models import Person

class PersonAdmin(admin.ModelAdmin):
	prepopulated_fields = { 'slug': ( 'first_name', 'last_name' ) }

admin.site.register(Person, PersonAdmin)

