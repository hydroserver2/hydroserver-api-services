from django.contrib import admin
from iam.models import User, UserType, Organization, Workspace, Role, Permission, Collaborator


class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "is_private")


class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "workspace__name")


class CollaboratorAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "role__name", "workspace__name")


admin.site.register(User)
admin.site.register(Organization)
admin.site.register(UserType)
admin.site.register(Workspace, WorkspaceAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Permission)
admin.site.register(Collaborator, CollaboratorAdmin)
