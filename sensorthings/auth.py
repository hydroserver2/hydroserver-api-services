from typing import Sequence
from django.contrib.auth import authenticate
from ninja.security import HttpBasicAuth
from sites.models import ThingAssociation
from hydrothings import SensorThingsRequest


class BasicAuth(HttpBasicAuth):
    def authenticate(self, request, username, password):
        user = authenticate(username=username, password=password)
        if user and user.is_authenticated:
            return user


def observation_authorization(request: SensorThingsRequest, **kwargs):
    """
    Checks user authentication for observation resources.

    Parameters
    ----------
    request : SensorThingsRequest
        The SensorThings request object.
    kwargs
        Keyword arguments that will be passed to the view function.

    Returns
    -------
    bool
        Returns True if the authenticated user has permission to modify the observation, otherwise returns False.
    """

    if request.method == 'POST':
        observation = kwargs['observation']

        if isinstance(observation, Sequence):
            datastream_id_list = [
                obs.datastream.id for obs in observation
            ]
        else:
            datastream_id_list = [observation.datastream.id]

        associations = ThingAssociation.objects.filter(
            thing__datastreams__id__in=datastream_id_list
        ).filter(
            person__email=request.auth
        ).filter(
            owns_thing=True
        )

        if len(associations) != len(datastream_id_list):
            return False
        else:
            return True

    elif request.method == 'DELETE':
        observation_id = kwargs['observation_id']

        associations = ThingAssociation.objects.filter(
            thing__datastreams__observation=observation_id
        ).filter(
            person__email=request.auth
        ).filter(
            owns_thing=True
        )

        if not associations:
            return False
        else:
            return True

    else:
        return False
