from django.contrib import admin
from models import Production, ProductionCompany, Part, Performance

class CompanyAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('name',),
    }

#class PartInline(admin.TabularInline):
#	model = Part
#	extra = 1
#
#class ProductionAdmin(admin.ModelAdmin):
#	inlines = [
#		PartInline,
#	]

admin.site.register(Production) # , ProductionAdmin)
admin.site.register(ProductionCompany, CompanyAdmin)
admin.site.register(Part)
admin.site.register(Performance)


