import os
import re
import uuid
import tempfile
import hsclient
from typing import Optional
from hsmodels.schemas.fields import PointCoverage
from allauth.socialaccount.models import SocialToken
from django.db import transaction
from django_tasks import task
from sta.services import DatastreamService
from sta.models import Datastream, Thing
from etl.models import DataArchive

datastream_service = DatastreamService()


@task()
@transaction.atomic
def archive_to_hydroshare(
    hs_client_id: str,
    hs_access_token_id: int,
    hs_archive_id: str,
    hs_resource_metadata: Optional[dict] = None,
):
    hs_archive = DataArchive.objects.get(pk=hs_archive_id)
    hs_access_token = SocialToken.objects.values_list("token", flat=True).get(id=hs_access_token_id)

    thing = Thing.objects.with_location().get(id=uuid.UUID(hs_archive.settings["thingId"]))

    hs_conn = hsclient.HydroShare(
        client_id=hs_client_id,
        token={
            "access_token": hs_access_token,
            "token_type": "Bearer",
        },
    )

    if hs_resource_metadata:
        archive_resource = hs_conn.create()
        archive_resource.metadata.title = hs_resource_metadata["resource_title"]
        archive_resource.metadata.abstract = hs_resource_metadata["resource_abstract"]
        archive_resource.metadata.subjects = hs_resource_metadata["resource_keywords"]
        archive_resource.metadata.spatial_coverage = PointCoverage(
            name=thing.location.name,
            north=thing.location.latitude,
            east=thing.location.longitude,
            projection="WGS 84 EPSG:4326",
            type="point",
            units="Decimal degrees",
        )
        archive_resource.metadata.additional_metadata = {
            "Sampling Feature Type": thing.sampling_feature_type,
            "Sampling Feature Code": thing.sampling_feature_code,
            "Site Type": thing.site_type,
        }
        archive_resource.save()
        hs_archive.settings["link"] = f"https://www.hydroshare.org/resource/{archive_resource.resource_id}/",
        hs_archive.save()
    else:
        archive_resource = hs_conn.resource(hs_archive.settings["link"])

    archive_folder = hs_archive.settings["path"].strip()

    if not archive_folder.endswith("/"):
        archive_folder += "/"

    if archive_folder == "/":
        archive_folder = ""

    datastreams = (
        Datastream.objects.filter(
            data_archives=hs_archive, pk__in=hs_archive.settings["datastreamIds"]
        ).select_related("processing_level", "observed_property").all()
    )

    processing_levels = {}

    for datastream in datastreams:
        if datastream.processing_level.code in processing_levels:
            processing_levels[datastream.processing_level.code].append(datastream)
        else:
            processing_levels[datastream.processing_level.code] = [datastream]

    with tempfile.TemporaryDirectory() as temp_dir:
        for processing_level, datastreams in processing_levels.items():
            processing_level_directory = f"{archive_folder}{processing_level}"
            processing_level_directory = re.sub(
                r"\s+", "_", processing_level_directory
            )

            try:
                archive_resource.folder_delete(processing_level_directory)
            except (Exception,):
                pass

            archive_resource.folder_create(processing_level_directory)
            os.mkdir(os.path.join(temp_dir, processing_level))

            datastream_files = []

            for datastream in datastreams:
                file_name = f"{datastream.observed_property.code}.csv"
                file_index = 2

                while file_name in datastream_files:
                    file_name = (
                        f"{datastream.observed_property.code}_{str(file_index)}.csv"
                    )
                    file_index += 1

                datastream_files.append(file_name)

                temp_file_path = os.path.join(temp_dir, processing_level, file_name)
                with open(temp_file_path, "w") as csv_file:
                    for line in datastream_service.generate_csv(datastream):
                        csv_file.write(line)

            datastream_file_paths = [
                os.path.join(temp_dir, processing_level, datastream_file)
                for datastream_file in datastream_files
            ]

            if datastream_file_paths:
                archive_resource.file_upload(
                    *datastream_file_paths,
                    destination_path=processing_level_directory,
                )

        if hs_resource_metadata and hs_resource_metadata.get("public_resource") is True:
            archive_resource.set_sharing_status(public=True)
            archive_resource.save()
