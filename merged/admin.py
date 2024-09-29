from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from merged.utils import merge_thing, check_old_exists
from .models import Redirect


class RedirectAdmin(admin.ModelAdmin):
    list_display = ('id', 'old_link', 'old_if_possible', 'new_link', 'new_object', 'approved')
    list_filter = ('approved',)
    actions = ['bulk_merge', 'bulk_merge_reverse']

    def old_if_possible(self, row):
        return check_old_exists(row)

    def old_link(self, row):
        old = self.old_if_possible(row)
        if old:
            return format_html('<a href="{}">{}</a>', old.get_absolute_url(), row.old_base32())
        return row.old_base32()

    def new_link(self, row):
        return format_html('<a href="{}">{}</a>', row.new_object.get_absolute_url(), row.new_base32())

    def bulk_merge(self, request, queryset):
        for obj in queryset:
            if old := self.old_if_possible(obj):
                old_desc = str(old)  # Might get deleted
                merge_thing(obj.new_object, old, obj)
                self.message_user(request, "%s merged into %s" % (old_desc, obj.new_object))
    bulk_merge.short_description = 'Approve merge (old to new)'

    def bulk_merge_reverse(self, request, queryset):
        for obj in queryset:
            if old := self.old_if_possible(obj):
                new_desc = str(obj.new_object)  # Might get deleted
                merge_thing(old, obj.new_object, obj)
                self.message_user(request, "%s merged into %s" % (new_desc, old))
    bulk_merge_reverse.short_description = 'Approve merge (new to old)'

    def response_change(self, request, obj):
        if "_approve" in request.POST:
            if old := self.old_if_possible(obj):
                merge_thing(obj.new_object, old, obj)
            return HttpResponseRedirect(".")
        if "_approveBack" in request.POST:
            if old := self.old_if_possible(obj):
                merge_thing(old, obj.new_object, obj)
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)


admin.site.register(Redirect, RedirectAdmin)
