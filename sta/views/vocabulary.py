from ninja import Router, Query
from django.http import HttpResponse
from sta.models import (
    SiteType,
    SamplingFeatureType,
    SensorEncodingType,
    MethodType,
    VariableType,
    UnitType,
    DatastreamStatus,
    DatastreamAggregation,
    SampledMedium,
)
from hydroserver.http import HydroServerHttpRequest
from hydroserver.service import VocabularyService
from hydroserver.schemas import VocabularyQueryParameters

sta_vocabulary_router = Router(tags=["Vocabulary"])
vocabulary_service = VocabularyService()


@sta_vocabulary_router.get(
    "things/site-types", response={200: list[str]}, by_alias=True
)
def get_site_types(
    request: HydroServerHttpRequest,
    response: HttpResponse,
    query: Query[VocabularyQueryParameters],
):
    """
    Get site types.
    """

    return 200, vocabulary_service.list(
        vocabulary_model=SiteType,
        response=response,
        page=query.page,
        page_size=query.page_size,
        order_desc=query.order_desc,
    )


@sta_vocabulary_router.get(
    "things/sampling-feature-types", response={200: list[str]}, by_alias=True
)
def get_sampling_feature_types(
    request: HydroServerHttpRequest,
    response: HttpResponse,
    query: Query[VocabularyQueryParameters],
):
    """
    Get sampling feature types.
    """

    return 200, vocabulary_service.list(
        vocabulary_model=SamplingFeatureType,
        response=response,
        page=query.page,
        page_size=query.page_size,
        order_desc=query.order_desc,
    )


@sta_vocabulary_router.get(
    "sensors/encoding-types", response={200: list[str]}, by_alias=True
)
def get_sensor_encoding_types(
    request: HydroServerHttpRequest,
    response: HttpResponse,
    query: Query[VocabularyQueryParameters],
):
    """
    Get sensor encoding types.
    """

    return 200, vocabulary_service.list(
        vocabulary_model=SensorEncodingType,
        response=response,
        page=query.page,
        page_size=query.page_size,
        order_desc=query.order_desc,
    )


@sta_vocabulary_router.get(
    "sensors/method-types", response={200: list[str]}, by_alias=True
)
def get_method_types(
    request: HydroServerHttpRequest,
    response: HttpResponse,
    query: Query[VocabularyQueryParameters],
):
    """
    Get method types.
    """

    return 200, vocabulary_service.list(
        vocabulary_model=MethodType,
        response=response,
        page=query.page,
        page_size=query.page_size,
        order_desc=query.order_desc,
    )


@sta_vocabulary_router.get(
    "observed-properties/variable-types", response={200: list[str]}, by_alias=True
)
def get_variable_types(
    request: HydroServerHttpRequest,
    response: HttpResponse,
    query: Query[VocabularyQueryParameters],
):
    """
    Get variable types.
    """

    return 200, vocabulary_service.list(
        vocabulary_model=VariableType,
        response=response,
        page=query.page,
        page_size=query.page_size,
        order_desc=query.order_desc,
    )


@sta_vocabulary_router.get("units/types", response={200: list[str]}, by_alias=True)
def get_unit_types(
    request: HydroServerHttpRequest,
    response: HttpResponse,
    query: Query[VocabularyQueryParameters],
):
    """
    Get unit types.
    """

    return 200, vocabulary_service.list(
        vocabulary_model=UnitType,
        response=response,
        page=query.page,
        page_size=query.page_size,
        order_desc=query.order_desc,
    )


@sta_vocabulary_router.get(
    "datastreams/statuses", response={200: list[str]}, by_alias=True
)
def get_datastream_statuses(
    request: HydroServerHttpRequest,
    response: HttpResponse,
    query: Query[VocabularyQueryParameters],
):
    """
    Get datastream statuses.
    """

    return 200, vocabulary_service.list(
        vocabulary_model=DatastreamStatus,
        response=response,
        page=query.page,
        page_size=query.page_size,
        order_desc=query.order_desc,
    )


@sta_vocabulary_router.get(
    "datastreams/aggregations", response={200: list[str]}, by_alias=True
)
def get_datastream_aggregations(
    request: HydroServerHttpRequest,
    response: HttpResponse,
    query: Query[VocabularyQueryParameters],
):
    """
    Get datastream aggregations.
    """

    return 200, vocabulary_service.list(
        vocabulary_model=DatastreamAggregation,
        response=response,
        page=query.page,
        page_size=query.page_size,
        order_desc=query.order_desc,
    )


@sta_vocabulary_router.get(
    "datastreams/sampled-mediums", response={200: list[str]}, by_alias=True
)
def get_sampled_mediums(
    request: HydroServerHttpRequest,
    response: HttpResponse,
    query: Query[VocabularyQueryParameters],
):
    """
    Get sampled mediums.
    """

    return 200, vocabulary_service.list(
        vocabulary_model=SampledMedium,
        response=response,
        page=query.page,
        page_size=query.page_size,
        order_desc=query.order_desc,
    )
