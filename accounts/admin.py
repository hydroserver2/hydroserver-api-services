from django.contrib import admin
from django.apps import AppConfig
from .models import CustomUser

admin.site.register(CustomUser)
