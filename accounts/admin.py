from django.contrib import admin
from django.apps import AppConfig
from .models import CustomUser, Organization, Membership

admin.site.register(CustomUser)
admin.site.register(Organization)
admin.site.register(Membership)
