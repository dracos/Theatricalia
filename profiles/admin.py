from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from models import Profile

admin.site.unregister(User)

class ProfileInline(admin.StackedInline):
    model = Profile

class MyUserAdmin(UserAdmin):
    inlines = [ ProfileInline ]
    list_display = ('username', 'email', 'name', 'is_staff', 'email_validated')

    def email_validated(self, obj):
        return obj.get_profile().email_validated
    email_validated.boolean = True

admin.site.register(User, MyUserAdmin)

