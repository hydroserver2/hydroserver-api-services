import uuid
from django.db import models
from django.db.models import Q
from simple_history.models import HistoricalRecords
from ninja.errors import HttpError
from accounts.models import Person


class ProcessingLevelQuerySet(models.QuerySet):

    def apply_permissions(self, user, method, model='ProcessingLevel'):
        if not user or not user.permissions.enabled():
            return self

        permission_filters = []

        for permission in user.permissions.get(model=model, method=method):
            for resource in permission.resources:
                if resource.model == 'ProcessingLevel':
                    if method != 'GET':
                        permission_filters.append(Q(id__in=resource.ids))

        return self.filter(*permission_filters) if permission_filters else self

    def get_by_id(self, processing_level_id, user, method, model='ProcessingLevel', raise_404=False, fetch=True):
        queryset = self.select_related('person')
        queryset = queryset.filter(Q(person__isnull=True) | Q(person__is_active=True))

        if model == 'ProcessingLevel' and method in ['POST', 'PATCH', 'DELETE']:
            queryset = queryset.filter(person=user)
        elif model == 'Datastream' and method in ['POST', 'PATCH']:
            queryset = queryset.filter(person=user)
        elif model == 'ProcessingLevel' and method == 'GET':
            pass
        else:
            raise ValueError('Unsupported method or model provided.')

        if user and user.permissions.enabled():
            queryset = queryset.apply_permissions(user=user, method=method, model=model)  # noqa

        try:
            if fetch is True:
                processing_level = queryset.distinct().get(pk=processing_level_id)
            else:
                processing_level = queryset.distinct().filter(pk=processing_level_id).exists()
        except ProcessingLevel.DoesNotExist:
            processing_level = None

        if not processing_level and raise_404:
            raise HttpError(404, 'Processing level not found.')

        return processing_level


class ProcessingLevel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='processing_levels', null=True,
                               blank=True, db_column='personId')
    code = models.CharField(max_length=255)
    definition = models.TextField(null=True, blank=True)
    explanation = models.TextField(null=True, blank=True)
    history = HistoricalRecords(custom_model_name='ProcessingLevelChangeLog', related_name='log')

    objects = ProcessingLevelQuerySet.as_manager()

    class Meta:
        db_table = 'ProcessingLevel'
