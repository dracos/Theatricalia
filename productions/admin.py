from django.contrib import admin
from django import forms
from reversion.admin import VersionAdmin
from .models import Production, ProductionCompany, Part, Place, Production_Companies, Visit
from .forms import AutoCompleteMultiValueField
from plays.models import Play
from autocomplete.widgets import AutocompleteModelAdmin, ForeignKeySearchInput


class CompanyAdmin(VersionAdmin):
    prepopulated_fields = {
        'slug': ('name',),
    }


class PartAdmin(VersionAdmin):
    search_fields = ['person__first_name', 'person__last_name']
    raw_id_fields = ('production', 'person')


class PartInline(admin.TabularInline):  # options.InlineModelAdmin):
    model = Part
    raw_id_fields = ('person',)
    extra = 1


class PlaceInline(admin.TabularInline):
    model = Place
    raw_id_fields = ('production', 'place')
    extra = 1


class CompanyInline(admin.TabularInline):  # options.InlineModelAdmin):
    model = Production_Companies
    raw_id_fields = ('productioncompany',)
    extra = 1


class VisitInline(admin.TabularInline):  # options.InlineModelAdmin):
    model = Visit
    # raw_id_fields = ('productioncompany',)
    extra = 1


class ProductionForm(forms.ModelForm):
    play = AutoCompleteMultiValueField(
            Play, 'title',
            fields=(forms.CharField(), forms.ModelChoiceField(Play.objects.all())),
            widget=ForeignKeySearchInput(Production.play.field.remote_field, ('title',))
    )

    class Meta:
        model = Production
        fields = "__all__"


class ProductionAdmin(VersionAdmin, AutocompleteModelAdmin):
    form = ProductionForm
    search_fields = ['play__title', 'places__name', 'companies__name']
    related_search_fields = {
        # 'places': ('name',),
        'play': ('title',),
    }
    inlines = [
        PartInline,
        PlaceInline,
        CompanyInline,
        VisitInline,
    ]

    def get_queryset(self, request):
        if request.user.is_superuser:
            return Production.all_objects.all()
        return super(ProductionAdmin, self).get_queryset(request)


class PlaceAdmin(VersionAdmin):
    raw_id_fields = ('production', 'place')


class Production_CompaniesAdmin(VersionAdmin):
    raw_id_fields = ('production', 'productioncompany')


admin.site.register(Production, ProductionAdmin)
admin.site.register(ProductionCompany, CompanyAdmin)
admin.site.register(Part, PartAdmin)
admin.site.register(Production_Companies, Production_CompaniesAdmin)
admin.site.register(Place, PlaceAdmin)
