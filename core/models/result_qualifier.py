import uuid
from django.db import models, IntegrityError
from django.db.models import Q
from simple_history.models import HistoricalRecords
from ninja.errors import HttpError
from accounts.models import Person
from core.models import Observation
from core.schemas.result_qualifier import ResultQualifierFields


class ResultQualifierQuerySet(models.QuerySet):

    def apply_permissions(self, user, method, model='ResultQualifier'):
        if not user or not user.permissions.enabled():
            return self

        permission_filters = []

        for permission in user.permissions.get(model=model, method=method):
            for resource in permission.resources:
                if resource.model == 'ResultQualifier':
                    if method != 'GET':
                        permission_filters.append(Q(id__in=resource.ids))

        return self.filter(*permission_filters) if permission_filters else self

    def get_by_id(self, result_qualifier_id, user, method, model='ResultQualifier', raise_404=False, fetch=True):
        queryset = self.select_related('person')
        queryset = queryset.filter(Q(person__isnull=True) | Q(person__is_active=True))

        if method != 'GET':
            queryset = queryset.filter(person=user)

            if user and user.permissions.enabled():
                queryset = queryset.apply_permissions(user=user, method=method, model=model)  # noqa

        try:
            if fetch is True:
                result_qualifier = queryset.distinct().get(pk=result_qualifier_id)
            else:
                result_qualifier = queryset.distinct().filter(pk=result_qualifier_id).exists()
        except ResultQualifier.DoesNotExist:
            result_qualifier = None

        if not result_qualifier and raise_404:
            raise HttpError(404, 'Result qualifier not found.')

        return result_qualifier


class ResultQualifier(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=255)
    description = models.TextField()
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='result_qualifiers', null=True,
                               blank=True, db_column='personId')
    history = HistoricalRecords(custom_model_name='ResultQualifierChangeLog', related_name='log')

    objects = ResultQualifierQuerySet.as_manager()

    def delete(self, using=None, keep_parents=False):
        if Observation.objects.filter(result_qualifiers__contains=[self.id]).exists():
            raise IntegrityError(
                f'Cannot delete result qualifier {str(self.id)} because it is referenced by one or more observations.'
            )
        else:
            super().delete(using=using, keep_parents=keep_parents)

    def serialize(self):
        return {
            'id': self.id,
            'owner': self.person.email if self.person else None,
            **{field: getattr(self, field) for field in ResultQualifierFields.__fields__.keys()},
        }

    class Meta:
        db_table = 'ResultQualifier'
