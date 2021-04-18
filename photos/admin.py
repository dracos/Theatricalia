from django.contrib import admin
from django.utils.html import mark_safe
from reversion.admin import VersionAdmin
from .models import Photo


@admin.register(Photo)
class PhotoAdmin(VersionAdmin):
    search_fields = ('title', 'author', 'source', 'license')
    list_filter = ('is_visible', 'content_type', 'license')
    list_display = ('title', 'author', 'is_visible', 'source_link')

    def source_link(self, obj):
        return mark_safe('<a class="grp-button" href="%s" target="_blank">Source</a>' % (obj.source,))

    def get_queryset(self, request):
        if request.user.is_superuser:
            return Photo.all_objects.all()
        return super(PhotoAdmin, self).get_queryset(request)
