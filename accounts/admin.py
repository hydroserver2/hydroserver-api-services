from django.contrib import admin
from .models import Person, PersonType, Organization

admin.site.register(Person)
admin.site.register(Organization)
admin.site.register(PersonType)
