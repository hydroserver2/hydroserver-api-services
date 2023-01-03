from ninja import Router, Query
from ninja.security import django_auth
from sensorthings.api.schemas import Filters


router = Router()


@router.get(
    '/FeaturesOfInterest/',
    auth=django_auth,
    tags=['Features Of Interest']
)
def get_features_of_interest(request, filters: Filters = Query(...)):
    """"""

    return {}


@router.get(
    '/FeaturesOfInterest({feature_of_interest_id})/',
    auth=django_auth,
    tags=['Features Of Interest']
)
def get_feature_of_interest(request, feature_of_interest_id: str):
    """"""

    return {}


@router.post(
    '/FeaturesOfInterest/',
    auth=django_auth,
    tags=['Features Of Interest']
)
def create_feature_of_interest(request):
    """"""

    return {}


@router.patch(
    '/FeaturesOfInterest({feature_of_interest_id})/',
    auth=django_auth,
    tags=['Features Of Interest']
)
def update_feature_of_interest(request, feature_of_interest_id: str):
    """"""

    return {}


@router.delete(
    '/FeaturesOfInterest({feature_of_interest_id})/',
    auth=django_auth,
    tags=['Features Of Interest']
)
def delete_feature_of_interest(request, feature_of_interest_id: str):
    """"""

    return {}
