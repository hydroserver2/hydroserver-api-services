import uuid
import boto3
import os
import tempfile
import requests
from datetime import datetime
from typing import Optional
from django.db import models
from django.db.models import Q, Prefetch
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from hsmodels.schemas.fields import PointCoverage
from ninja.errors import HttpError
from simple_history.models import HistoricalRecords
from botocore.exceptions import ClientError
from core.models import Location
from core.utils import generate_csv
from hydroserver import settings


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


class Thing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    sampling_feature_type = models.CharField(max_length=200, db_column='samplingFeatureType')
    sampling_feature_code = models.CharField(max_length=200, db_column='samplingFeatureCode')
    site_type = models.CharField(max_length=200, db_column='siteType')
    is_private = models.BooleanField(default=False, db_column='isPrivate')
    data_disclaimer = models.TextField(null=True, blank=True, db_column='dataDisclaimer')
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


class ArchiveManager(models.Manager):
    def create_or_link(
            self,
            hs_connection,
            thing,
            resource_title=None,
            resource_abstract=None,
            resource_keywords=None,
            link=None,
            path='/',
            frequency=None,
            datastream_ids=None,
            public_resource=False
    ):

        if link:
            try:
                archive_resource = hs_connection.resource(link.split('/')[-2])
            except (Exception,):  # hsclient just raises a generic exception if the resource doesn't exist.
                raise HttpError(400, 'Provided HydroShare resource does not exist.')
        else:
            archive_resource = hs_connection.create()
            archive_resource.metadata.title = resource_title
            archive_resource.metadata.abstract = resource_abstract
            archive_resource.metadata.subjects = resource_keywords
            archive_resource.metadata.spatial_coverage = PointCoverage(
                name=thing.location.name,
                north=thing.location.latitude,
                east=thing.location.longitude,
                projection='WGS 84 EPSG:4326',
                type='point',
                units='Decimal degrees'
            )
            archive_resource.metadata.additional_metadata = {
                'Sampling Feature Type': thing.sampling_feature_type,
                'Sampling Feature Code': thing.sampling_feature_code,
                'Site Type': thing.site_type
            }

            if thing.data_disclaimer:
                archive_resource.metadata.additional_metadata['Data Disclaimer'] = thing.data_disclaimer

            archive_resource.save()

        for datastream in thing.datastreams.all():
            if datastream_ids and datastream.id in datastream_ids:
                datastream.archived = True
            else:
                datastream.archived = False

        archive = self.create(
            thing=thing,
            link=f'https://www.hydroshare.org/resource/{archive_resource.resource_id}/',
            path=path,
            frequency=frequency
        )
        archive.save()

        return archive


class Archive(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thing = models.OneToOneField('Thing', related_name='archive', on_delete=models.CASCADE, db_column='thingId')
    link = models.URLField(max_length=255)
    path = models.CharField(max_length=255)
    frequency = models.CharField(max_length=255, blank=True, null=True)

    objects = ArchiveManager()

    @property
    def datastream_ids(self):
        return [
            datastream['id'] for datastream in self.thing.datastreams.filter(archived=True).values('id').all()
        ]

    @property
    def public_resource(self):
        response = requests.get(f'{self.link.replace("resource", "hsapi/resource")}/sysmeta/')
        return response.status_code == 200

    def transfer_data(self, hs_connection, make_public=False):
        archive_resource = hs_connection.resource(self.link.split('/')[-2])
        archive_folder = self.path

        if not archive_folder.endswith('/'):
            archive_folder += '/'

        if archive_folder == '/':
            archive_folder = ''

        datastreams = self.thing.datastreams.filter(
            Q(thing_id=self.thing_id) & Q(archived=True)
        ).select_related('processing_level', 'observed_property').all()

        datastream_file_names = []

        processing_levels = list(set([
            datastream.processing_level.definition for datastream in datastreams
        ]))

        with tempfile.TemporaryDirectory() as temp_dir:
            for processing_level in processing_levels:
                try:
                    archive_resource.folder_delete(f'{archive_folder}{processing_level}')
                except (Exception,):
                    pass
                archive_resource.folder_create(f'{archive_folder}{processing_level}')
                os.mkdir(os.path.join(temp_dir, processing_level))
            for datastream in datastreams:
                temp_file_name = datastream.observed_property.code
                temp_file_index = 2
                while f'{datastream.processing_level.definition}_{temp_file_name}' in datastream_file_names:
                    temp_file_name = f'{datastream.observed_property.code} - {str(temp_file_index)}'
                    temp_file_index += 1
                datastream_file_names.append(f'{datastream.processing_level.definition}_{temp_file_name}')
                temp_file_name = f'{temp_file_name}.csv'
                temp_file_path = os.path.join(temp_dir, datastream.processing_level.definition, temp_file_name)
                with open(temp_file_path, 'w') as csv_file:
                    for line in generate_csv(datastream):
                        csv_file.write(line)
                archive_resource.file_upload(
                    temp_file_path,
                    destination_path=f'{archive_folder}{datastream.processing_level.definition}'
                )

            if make_public is True:
                try:
                    archive_resource.set_sharing_status(public=True)
                    archive_resource.save()
                except (Exception,):
                    pass

    class Meta:
        db_table = 'Archive'


@receiver(pre_delete, sender=Photo)
def delete_photo(sender, instance, **kwargs):
    s3 = boto3.client(
        's3',
        region_name='us-east-1',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )

    file_name = instance.link.split(f'{settings.PROXY_BASE_URL}/')[1]

    try:
        s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_name)
    except ClientError as e:
        print(f'Error deleting {file_name} from S3: {e}')
