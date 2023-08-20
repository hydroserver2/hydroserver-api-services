from django.db.models import Q
from django.http import JsonResponse
from ninja import Router, Schema

from sites.models import ObservedProperty
from sites.utils.authentication import jwt_auth
from sites.utils.observed_property import observed_property_to_dict

router = Router()


class ObservedPropertyInput(Schema):
    name: str
    definition: str
    description: str = None
    variable_type: str = None
    variable_code: str = None


@router.post('', auth=jwt_auth)
def create_observed_property(request, data: ObservedPropertyInput):
    observed_property = ObservedProperty.objects.create(
        name=data.name,
        person=request.authenticated_user,
        definition=data.definition,
        description=data.description,
        variable_type=data.variable_type,
        variable_code=data.variable_code
    )
    return JsonResponse(observed_property_to_dict(observed_property))


@router.get('', auth=jwt_auth)
def get_observed_properties(request):
    observed_properties = ObservedProperty.objects.filter(Q(person=request.authenticated_user) | Q(person__isnull=True))
    return JsonResponse([observed_property_to_dict(op) for op in observed_properties], safe=False)




@router.patch('/{observed_property_id}', auth=jwt_auth)
def update_observed_property(request, observed_property_id: str, data: ObservedPropertyInput):
    observed_property = ObservedProperty.objects.get(id=observed_property_id)
    if request.authenticated_user != observed_property.person:
        return JsonResponse({'detail': 'You are not authorized to update this observed property.'}, status=403)

    if data.name is not None:
        observed_property.name = data.name
    if data.definition is not None:
        observed_property.definition = data.definition
    if data.description is not None:
        observed_property.description = data.description
    if data.variable_type is not None:
        observed_property.variable_type = data.variable_type
    if data.variable_code is not None:
        observed_property.variable_code = data.variable_code

    observed_property.save()

    return JsonResponse(observed_property_to_dict(observed_property))


@router.delete('/{observed_property_id}', auth=jwt_auth)
def delete_observed_property(request, observed_property_id: str):
    try:
        observed_property = ObservedProperty.objects.get(id=observed_property_id)
    except ObservedProperty.DoesNotExist:
        return JsonResponse({'detail': 'Observed Property not found.'}, status=404)

    if request.authenticated_user != observed_property.person:
        return JsonResponse({'detail': 'You are not authorized to delete this observed property.'}, status=403)

    observed_property.delete()

    return {'detail': 'Observed Property deleted successfully.'}
