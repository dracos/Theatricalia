from django.contrib import admin
from reversion.admin import VersionAdmin
from models import Photo

admin.site.register(Photo, VersionAdmin)

