from django.contrib import admin
from models import Play

class PlayAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('title',),
    }

admin.site.register(Play, PlayAdmin)
