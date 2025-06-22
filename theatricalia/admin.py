from django.contrib import admin
from django.contrib.admin import ModelAdmin, StackedInline, TabularInline  # noqa: F401


class MyAdminSite(admin.AdminSite):
    site_header = "Theatricalia administration"


site = MyAdminSite()
