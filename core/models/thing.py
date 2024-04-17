import uuid
import boto3
from datetime import datetime
from typing import Optional
from django.db import models
from django.db.models import Q, Prefetch
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from ninja.errors import HttpError
from simple_history.models import HistoricalRecords
from botocore.exceptions import ClientError
from core.models import Location
from hydroserver.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, PROXY_BASE_URL


class ThingQuerySet(models.QuerySet):

    def apply_permissions(self, user, method, model='Thing'):
        if not user or not user.permissions.enabled():
            return self

        permission_filters = []

        for permission in user.permissions.get(model=model, method=method):
            for resource in permission.resources:
                if resource.model == 'Thing':
                    permission_filter = Q(id__in=resource.ids)
                    permission_filter |= Q(is_private=False) if method == 'GET' else Q()
                    permission_filters.append(permission_filter)

        return self.filter(*permission_filters) if permission_filters else self

    def owner_is_active(self):
        return self.filter(~(Q(associates__is_primary_owner=True) & Q(associates__person__is_active=False)))

    def primary_owner(self, user, include_public=False):
        query = Q(associates__person=user) & Q(associates__is_primary_owner=True)
        query |= Q(is_private=False) if include_public else Q()
        return self.filter(query)

    def owner(self, user, include_public=False):
        query = Q(associates__person=user) & Q(associates__owns_thing=True)
        query |= Q(is_private=False) if include_public else Q()
        return self.filter(query)

    def unaffiliated(self, user):
        return self.filter(~(Q(associates__person=user) & Q(associates__is_owner=True)))

    def follower(self, user):
        return self.filter(Q(associates__person=user) & Q(associates__follows_thing=True))

    def prefetch_associates(self):
        from core.models import ThingAssociation
        associates_prefetch = Prefetch(
            'associates', queryset=ThingAssociation.objects.select_related('person', 'person__organization')
        )
        return self.prefetch_related(associates_prefetch)

    def modified_since(self, modified: Optional[datetime] = None):
        return self.prefetch_related('log').filter(
           log__history_date__gt=modified
        ) if modified is not None else self

    def get_by_id(self, thing_id, user, method, model='Thing', raise_404=False, fetch=True, prefetch=None):
        queryset = self.select_related('location')
        queryset = queryset.prefetch_associates()  # noqa

        if prefetch:
            queryset = queryset.prefetch_related(*prefetch)

        queryset = queryset.owner_is_active()

        if model in ['Thing', 'Datastream'] and method == 'GET':
            queryset = queryset.owner(user=user, include_public=True)
        elif (model == 'Thing' and method == 'PATCH') or (model == 'Datastream' and method in ['POST', 'PATCH']):
            queryset = queryset.owner(user=user)
        elif model == 'Thing' and method == 'DELETE':
            queryset = queryset.primary_owner(user=user)
        else:
            raise ValueError('Unsupported method or model provided.')

        if user and user.permissions.enabled():
            queryset = queryset.apply_permissions(user=user, method=method, model=model)

        try:
            if fetch is True:
                thing = queryset.distinct().get(pk=thing_id)
            else:
                thing = queryset.distinct().filter(pk=thing_id).exists()
        except Thing.DoesNotExist:
            thing = None

        if not thing and raise_404:
            raise HttpError(404, 'Thing not found.')

        return thing

    # def get_primary_owner(self, thing_id, user=None, user_is_owner=False):
    #     queryset = self.prefetch_associates()  # noqa
    #     queryset = queryset.owner_is_active()
    #
    #     if user_is_owner is True:
    #         queryset = queryset.owner(user=user)
    #
    #     try:
    #         thing = queryset.distinct().get(pk=thing_id)
    #     except Thing.DoesNotExist:
    #         return None
    #
    #     primary_associate = thing.associates.get(is_primary_owner=True)
    #
    #     return primary_associate.person


class Thing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    sampling_feature_type = models.CharField(max_length=200, db_column='samplingFeatureType')
    sampling_feature_code = models.CharField(max_length=200, db_column='samplingFeatureCode')
    site_type = models.CharField(max_length=200, db_column='siteType')
    is_private = models.BooleanField(default=False, db_column='isPrivate')
    data_disclaimer = models.TextField(null=True, blank=True, db_column='dataDisclaimer')
    hydroshare_archive_resource_id = models.CharField(
        max_length=500, blank=True, null=True, db_column='hydroshareArchiveResourceId'
    )
    location = models.OneToOneField(Location, related_name='thing', on_delete=models.CASCADE, db_column='locationId')
    history = HistoricalRecords(custom_model_name='ThingChangeLog', related_name='log')

    objects = ThingQuerySet.as_manager()

    @property
    def primary_owner(self):
        return self.associates.get(is_primary_owner=True).person

    class Meta:
        db_table = 'Thing'


class Tag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thing = models.ForeignKey('Thing', related_name='tags', on_delete=models.CASCADE, db_column='thingId')
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    class Meta:
        db_table = 'Tag'
        unique_together = ('thing', 'key')


class Photo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thing = models.ForeignKey('Thing', related_name='photos', on_delete=models.CASCADE, db_column='thingId')
    file_path = models.CharField(max_length=1000, db_column='filePath')
    link = models.URLField(max_length=2000)
    history = HistoricalRecords(custom_model_name='PhotoChangeLog', related_name='log')

    class Meta:
        db_table = 'Photo'


@receiver(pre_delete, sender=Photo)
def delete_photo(sender, instance, **kwargs):
    s3 = boto3.client(
        's3',
        region_name='us-east-1',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    file_name = instance.link.split(f'{PROXY_BASE_URL}/')[1]

    try:
        s3.delete_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=file_name)
    except ClientError as e:
        print(f'Error deleting {file_name} from S3: {e}')
