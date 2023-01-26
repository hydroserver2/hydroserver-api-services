from django.contrib import admin
from .models import SensorModel, SensorManufacturer

admin.site.register(SensorModel)
admin.site.register(SensorManufacturer)
