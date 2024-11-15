from django.contrib import admin
from .models import UserType, CustomUser, Company

# Register your models here.
admin.site.register(UserType)
admin.site.register(CustomUser)
admin.site.register(Company)