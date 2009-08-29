from django.contrib import admin
from reversion.admin import VersionAdmin
from models import Alert, AlertLocal

class AlertAdmin(VersionAdmin):
    pass

admin.site.register(Alert, AlertAdmin)
admin.site.register(AlertLocal, AlertAdmin)

