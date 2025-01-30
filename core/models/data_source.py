import uuid
from django.db import models
from django.db.models import Q
from simple_history.models import HistoricalRecords
from ninja.errors import HttpError
from core.models import DataLoader
from django.contrib.auth import get_user_model

User = get_user_model()


class DataSourceQuerySet(models.QuerySet):

    def apply_permissions(self, user, method, model='DataSource'):
        if not user or not user.permissions.enabled():
            return self

        permission_filters = []

        for permission in user.permissions.get(model=model, method=method):
            for resource in permission.resources:
                if resource.model == 'DataSource':
                    permission_filters.append(Q(id__in=resource.ids))
                if resource.model == 'DataLoader':
                    permission_filters.append(Q(dataloader_id__in=resource.ids))

        return self.filter(*permission_filters) if permission_filters else self

    def get_by_id(self, data_source_id, user, method, model='DataSource', raise_404=False, fetch=True):
        queryset = self.select_related('person')
        queryset = queryset.filter(person__is_active=True)
        queryset = queryset.filter(person=user)

        if user and user.permissions.enabled():
            queryset = queryset.apply_permissions(user=user, method=method, model=model)  # noqa

        try:
            if fetch is True:
                data_source = queryset.distinct().get(pk=data_source_id)
            else:
                data_source = queryset.distinct().filter(pk=data_source_id).exists()
        except DataSource.DoesNotExist:
            data_source = None

        if not data_source and raise_404:
            raise HttpError(404, 'Data source not found.')

        return data_source


class DataSource(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255, null=True, blank=True)
    link = models.CharField(max_length=255, null=True, blank=True)
    header_row = models.PositiveIntegerField(null=True, blank=True, db_column='headerRow')
    data_start_row = models.PositiveIntegerField(null=True, blank=True, db_column='dataStartRow')
    delimiter = models.CharField(max_length=1, null=True, blank=True)
    quote_char = models.CharField(max_length=1, null=True, blank=True, db_column='quoteChar')
    interval = models.PositiveIntegerField(null=True, blank=True)
    interval_units = models.CharField(max_length=255, null=True, blank=True, db_column='intervalUnits')
    crontab = models.CharField(max_length=255, null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True, db_column='startTime')
    end_time = models.DateTimeField(null=True, blank=True, db_column='endTime')
    paused = models.BooleanField()
    timestamp_column = models.CharField(max_length=255, null=True, blank=True, db_column='timestampColumn')
    timestamp_format = models.CharField(max_length=255, null=True, blank=True, db_column='timestampFormat')
    timestamp_offset = models.CharField(max_length=255, null=True, blank=True, db_column='timestampOffset')
    data_loader = models.ForeignKey(
        DataLoader, on_delete=models.SET_NULL, null=True, blank=True, db_column='dataLoaderId'
    )
    data_source_thru = models.DateTimeField(null=True, blank=True, db_column='dataSourceThru')
    last_sync_successful = models.BooleanField(null=True, blank=True, db_column='lastSyncSuccessful')
    last_sync_message = models.TextField(null=True, blank=True, db_column='lastSyncMessage')
    last_synced = models.DateTimeField(null=True, blank=True, db_column='lastSynced')
    next_sync = models.DateTimeField(null=True, blank=True, db_column='nextSync')
    person = models.ForeignKey(User, on_delete=models.CASCADE, related_name='data_sources', db_column='personId')
    history = HistoricalRecords(custom_model_name='DataSourceChangeLog', related_name='log')

    objects = DataSourceQuerySet.as_manager()

    class Meta:
        db_table = 'DataSource'
