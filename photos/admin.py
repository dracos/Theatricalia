from django.contrib import admin
from reversion.admin import VersionAdmin
from models import Photo

@admin.register(Photo)
class PhotoAdmin(VersionAdmin):
    search_fields = ('title',)
    list_filter = ('is_visible',)
    list_display = ('title', 'is_visible')

    def get_queryset(self, request):
        if request.user.is_superuser:
            return Photo.all_objects.all()
        return super(PhotoAdmin, self).get_queryset(request)
