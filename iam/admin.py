from django.contrib import admin
from .models import User, UserType, Organization

admin.site.register(User)
admin.site.register(Organization)
admin.site.register(UserType)
