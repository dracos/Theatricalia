from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from models import Profile, User

class ProfileInline(admin.StackedInline):
    model = Profile

class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User

# Help from https://stackoverflow.com/questions/15012235/using-django-auth-useradmin-for-a-custom-user-model
class MyUserAdmin(UserAdmin):
    form = MyUserChangeForm

    fieldsets = ( ( "Personal data", { 'fields': ( 'name', ) } ), ) + UserAdmin.fieldsets

    inlines = [ ProfileInline ]
    list_display = ('username', 'email', 'name', 'is_staff', 'email_validated')

    def email_validated(self, obj):
        return obj.get_profile().email_validated
    email_validated.boolean = True

admin.site.register(User, MyUserAdmin)

