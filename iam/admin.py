from django.contrib import admin
from django.urls import path
from iam.models import (
    User,
    UserType,
    Organization,
    OrganizationType,
    Workspace,
    Role,
    Permission,
    Collaborator,
)
from hydroserver.admin import VocabularyAdmin


class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "account_type", "is_active")


class UserTypeAdmin(admin.ModelAdmin, VocabularyAdmin):
    list_display = ("id", "name")
    change_list_template = "admin/iam/usertype/change_list.html"

    def get_urls(self):
        urls = super().get_urls()

        return [
            path(
                "load-default-user-type-data/",
                self.admin_site.admin_view(self.load_default_data),
                name="user_type_load_default_data",
            ),
        ] + urls

    def load_default_data(self, request):
        return self.load_fixtures(
            request,
            "admin:iam_usertype_changelist",
            ["iam/fixtures/default_user_types.yaml"],
        )


class OrganizationTypeAdmin(admin.ModelAdmin, VocabularyAdmin):
    list_display = ("id", "name")
    change_list_template = "admin/iam/organizationtype/change_list.html"

    def get_urls(self):
        urls = super().get_urls()

        return [
            path(
                "load-default-organization-type-data/",
                self.admin_site.admin_view(self.load_default_data),
                name="organization_type_load_default_data",
            ),
        ] + urls

    def load_default_data(self, request):
        return self.load_fixtures(
            request,
            "admin:iam_organizationtype_changelist",
            ["iam/fixtures/default_organization_types.yaml"],
        )


class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "is_private")


class RoleAdmin(admin.ModelAdmin, VocabularyAdmin):
    list_display = ("id", "name", "workspace__name")
    change_list_template = "admin/iam/role/change_list.html"

    def get_urls(self):
        urls = super().get_urls()

        return [
            path(
                "load-default-role-data/",
                self.admin_site.admin_view(self.load_default_data),
                name="role_load_default_data",
            ),
        ] + urls

    def load_default_data(self, request):
        return self.load_fixtures(
            request, "admin:iam_role_changelist", ["iam/fixtures/default_roles.yaml"]
        )


class CollaboratorAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "role__name", "workspace__name")


admin.site.register(User, UserAdmin)
admin.site.register(Organization)
admin.site.register(UserType, UserTypeAdmin)
admin.site.register(OrganizationType, OrganizationTypeAdmin)
admin.site.register(Workspace, WorkspaceAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Permission)
admin.site.register(Collaborator, CollaboratorAdmin)
