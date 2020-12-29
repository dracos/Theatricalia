from django.contrib import admin
from .models import Alert, AlertLocal, AlertSent


class AlertAdmin(admin.ModelAdmin):
    pass


admin.site.register(Alert, AlertAdmin)
admin.site.register(AlertLocal, AlertAdmin)
admin.site.register(AlertSent, AlertAdmin)
