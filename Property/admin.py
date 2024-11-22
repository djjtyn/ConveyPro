from django.contrib import admin
from .models import Country, Property, Opportunity, Stage, Country, Development, Note

class DateFields(admin.ModelAdmin):
    readonly_fields = ('last_modified_date', )


admin.site.register(Country)
admin.site.register(Property)
admin.site.register(Opportunity, DateFields)
admin.site.register(Stage)
admin.site.register(Development)
admin.site.register(Note)