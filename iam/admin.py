from django.contrib import admin
from iam.models import User, UserType, Organization, Workspace, Role, Permission, Collaborator

admin.site.register(User)
admin.site.register(Organization)
admin.site.register(UserType)
admin.site.register(Workspace)
admin.site.register(Role)
admin.site.register(Permission)
admin.site.register(Collaborator)
