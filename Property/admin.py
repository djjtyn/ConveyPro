from django.contrib import admin
from .models import *

class DateFields(admin.ModelAdmin):
    readonly_fields = ('last_modified_date', )


admin.site.register(Country)
admin.site.register(Property)
admin.site.register(Opportunity, DateFields)
admin.site.register(Stage)
admin.site.register(Development)
admin.site.register(Note)
admin.site.register(LocalDocument)
admin.site.register(ChangeType)
admin.site.register(ChangeAudit)