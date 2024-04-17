import uuid
from django.db import models
from django.db.models import Q
from simple_history.models import HistoricalRecords
from ninja.errors import HttpError
from accounts.models import Person


class ObservedPropertyQuerySet(models.QuerySet):

    def apply_permissions(self, user, method, model='ObservedProperty'):
        if not user or not user.permissions.enabled():
            return self

        permission_filters = []

        for permission in user.permissions.get(model=model, method=method):
            for resource in permission.resources:
                if resource.model == 'ObservedProperty':
                    if method != 'GET':
                        permission_filters.append(Q(id__in=resource.ids))

        return self.filter(*permission_filters) if permission_filters else self

    def get_by_id(self, observed_property_id, user, method, model='ObservedProperty', raise_404=False, fetch=True):
        queryset = self.select_related('person')
        queryset = queryset.filter(Q(person__isnull=True) | Q(person__is_active=True))

        if model == 'ObservedProperty' and method in ['POST', 'PATCH', 'DELETE']:
            queryset = queryset.filter(person=user)
        elif model == 'Datastream' and method in ['POST', 'PATCH']:
            queryset = queryset.filter(person=user)
        elif model == 'ObservedProperty' and method == 'GET':
            pass
        else:
            raise ValueError('Unsupported method or model provided.')

        if user and user.permissions.enabled():
            queryset = queryset.apply_permissions(user=user, method=method, model=model)  # noqa

        try:
            if fetch is True:
                observed_property = queryset.distinct().get(pk=observed_property_id)
            else:
                observed_property = queryset.distinct().filter(pk=observed_property_id).exists()
        except ObservedProperty.DoesNotExist:
            observed_property = None

        if not observed_property and raise_404:
            raise HttpError(404, 'Observed property not found.')

        return observed_property


class ObservedProperty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True, db_column='personId')
    name = models.CharField(max_length=255)
    definition = models.TextField()
    description = models.TextField()
    type = models.CharField(max_length=500)
    code = models.CharField(max_length=500)
    history = HistoricalRecords(custom_model_name='ObservedPropertyChangeLog', related_name='log')

    objects = ObservedPropertyQuerySet.as_manager()

    class Meta:
        db_table = 'ObservedProperty'
