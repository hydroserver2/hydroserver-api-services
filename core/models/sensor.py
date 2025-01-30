import uuid
from django.db import models
from django.db.models import Q
from simple_history.models import HistoricalRecords
from ninja.errors import HttpError
from django.contrib.auth import get_user_model

User = get_user_model()


class SensorQuerySet(models.QuerySet):

    def apply_permissions(self, user, method, model='Sensor'):
        if not user or not user.permissions.enabled():
            return self

        permission_filters = []

        for permission in user.permissions.get(model=model, method=method):
            for resource in permission.resources:
                if resource.model == 'Sensor':
                    if method != 'GET':
                        permission_filters.append(Q(id__in=resource.ids))

        return self.filter(*permission_filters) if permission_filters else self

    def get_by_id(self, sensor_id, user, method, model='Sensor', raise_404=False, fetch=True):
        queryset = self.select_related('person')
        queryset = queryset.filter(Q(person__isnull=True) | Q(person__is_active=True))

        if model == 'Sensor' and method in ['POST', 'PATCH', 'DELETE']:
            queryset = queryset.filter(person=user)
        elif model == 'Datastream' and method in ['POST', 'PATCH']:
            queryset = queryset.filter(person=user)
        elif model == 'Sensor' and method == 'GET':
            pass
        else:
            raise ValueError('Unsupported method or model provided.')

        if user and user.permissions.enabled():
            queryset = queryset.apply_permissions(user=user, method=method, model=model)  # noqa

        try:
            if fetch is True:
                sensor = queryset.distinct().get(pk=sensor_id)
            else:
                sensor = queryset.distinct().filter(pk=sensor_id).exists()
        except Sensor.DoesNotExist:
            sensor = None

        if not sensor and raise_404:
            raise HttpError(404, 'Sensor not found.')

        return sensor


class Sensor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, db_column='personId')
    name = models.CharField(max_length=255)
    description = models.TextField()
    encoding_type = models.CharField(max_length=255, db_column='encodingType')
    manufacturer = models.CharField(max_length=255, null=True, blank=True)
    model = models.CharField(max_length=255, null=True, blank=True)
    model_link = models.CharField(max_length=500, null=True, blank=True, db_column='modelLink')
    method_type = models.CharField(max_length=100, db_column='methodType')
    method_link = models.CharField(max_length=500, blank=True, null=True, db_column='methodLink')
    method_code = models.CharField(max_length=50, blank=True, null=True, db_column='methodCode')
    history = HistoricalRecords(custom_model_name='SensorChangeLog', related_name='log')

    objects = SensorQuerySet.as_manager()

    def __str__(self):
        if self.method_type and self.method_type.strip().lower().replace(" ", "") == 'instrumentdeployment':
            return f"{self.manufacturer}:{self.model}"
        else:
            return f"{self.method_type}:{self.method_code}"

    class Meta:
        db_table = 'Sensor'
