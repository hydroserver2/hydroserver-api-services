from ninja import Router
from sta.models import (SiteType, SamplingFeatureType, SensorEncodingType, MethodType, VariableType, UnitType,
                        DatastreamStatus, DatastreamAggregation, SampledMedium)

sta_vocabulary_router = Router(tags=["Vocabulary"])


@sta_vocabulary_router.get(
    "things/site-types",
    response={
        200: list[str]
    },
    by_alias=True
)
def get_site_types(request):
    """
    Get site types.
    """

    return 200, SiteType.objects.values_list("name", flat=True)


@sta_vocabulary_router.get(
    "things/sampling-feature-types",
    response={
        200: list[str]
    },
    by_alias=True
)
def get_sampling_feature_types(request):
    """
    Get sampling feature types.
    """

    return 200, SamplingFeatureType.objects.values_list("name", flat=True)


@sta_vocabulary_router.get(
    "sensors/encoding-types",
    response={
        200: list[str]
    },
    by_alias=True
)
def get_sensor_encoding_types(request):
    """
    Get sensor encoding types.
    """

    return 200, SensorEncodingType.objects.values_list("name", flat=True)


@sta_vocabulary_router.get(
    "sensors/method-types",
    response={
        200: list[str]
    },
    by_alias=True
)
def get_method_types(request):
    """
    Get method types.
    """

    return 200, MethodType.objects.values_list("name", flat=True)


@sta_vocabulary_router.get(
    "observed-properties/variable-types",
    response={
        200: list[str]
    },
    by_alias=True
)
def get_variable_types(request):
    """
    Get variable types.
    """

    return 200, VariableType.objects.values_list("name", flat=True)


@sta_vocabulary_router.get(
    "units/types",
    response={
        200: list[str]
    },
    by_alias=True
)
def get_unit_types(request):
    """
    Get unit types.
    """

    return 200, UnitType.objects.values_list("name", flat=True)


@sta_vocabulary_router.get(
    "datastreams/statuses",
    response={
        200: list[str]
    },
    by_alias=True
)
def get_datastream_statuses(request):
    """
    Get datastream statuses.
    """

    return 200, DatastreamStatus.objects.values_list("name", flat=True)


@sta_vocabulary_router.get(
    "datastreams/aggregations",
    response={
        200: list[str]
    },
    by_alias=True
)
def get_datastream_aggregations(request):
    """
    Get datastream aggregations.
    """

    return 200, DatastreamAggregation.objects.values_list("name", flat=True)


@sta_vocabulary_router.get(
    "datastreams/sampled-mediums",
    response={
        200: list[str]
    },
    by_alias=True
)
def get_sampled_mediums(request):
    """
    Get sampled mediums.
    """

    return 200, SampledMedium.objects.values_list("name", flat=True)
