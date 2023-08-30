from django.contrib import admin
from .models import CustomUser, Organization

admin.site.register(CustomUser)
admin.site.register(Organization)
