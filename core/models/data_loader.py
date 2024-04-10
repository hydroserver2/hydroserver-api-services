import uuid
from django.db import models
from django.db.models import Q
from simple_history.models import HistoricalRecords
from ninja.errors import HttpError
from accounts.models import Person
from core.schemas.data_loader import DataLoaderFields


class DataLoaderQuerySet(models.QuerySet):

    def apply_permissions(self, user, method, model='DataLoader'):
        if not user or not user.permissions.enabled():
            return self

        permission_filters = []

        for permission in user.permissions.get(model=model, method=method):
            for resource in permission.resources:
                if resource.model == 'DataLoader':
                    permission_filters.append(Q(id__in=resource.ids))

        return self.filter(*permission_filters) if permission_filters else self

    def get_by_id(self, data_loader_id, user, method, model='DataLoader', raise_404=False, fetch=True):
        queryset = self.select_related('person')
        queryset = queryset.filter(person__is_active=True)
        queryset = queryset.filter(person=user)

        if user and user.permissions.enabled():
            queryset = queryset.apply_permissions(user=user, method=method, model=model)  # noqa

        try:
            if fetch is True:
                data_loader = queryset.distinct().get(pk=data_loader_id)
            else:
                data_loader = queryset.distinct().filter(pk=data_loader_id).exists()
        except DataLoader.DoesNotExist:
            data_loader = None

        if not data_loader and raise_404:
            raise HttpError(404, 'Data loader not found.')

        return data_loader


class DataLoader(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='data_loaders', db_column='personId')
    history = HistoricalRecords(custom_model_name='DataLoaderChangeLog', related_name='log')

    objects = DataLoaderQuerySet.as_manager()

    def serialize(self):
        return {
            'id': self.id,
            **{field: getattr(self, field) for field in DataLoaderFields.__fields__.keys()},
        }

    class Meta:
        db_table = 'DataLoader'
