from django.db import models


class Organization(models.Model):
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    link = models.URLField(max_length=2000, blank=True, null=True)
    _organization_type = models.ForeignKey("OrganizationType", on_delete=models.SET_NULL, blank=True, null=True,
                                           db_column="organization_type_id")

    @property
    def organization_type(self):
        return self._organization_type.name if self._organization_type else None

    @organization_type.setter
    def organization_type(self, value):
        try:
            self._organization_type = None if value is None else OrganizationType.objects.get(name=value)
        except OrganizationType.DoesNotExist:
            raise ValueError(f"'{value}' is not an allowed user type.")


class OrganizationType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    public = models.BooleanField(default=True)

    def __str__(self):
        return self.name
