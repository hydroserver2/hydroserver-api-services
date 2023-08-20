from django.http import JsonResponse
from django.db.models import Q

from ninja import Router, Schema

from sites.models import Unit
from sites.utils.unit import unit_to_dict
from sites.utils.authentication import jwt_auth


router = Router()


class CreateUnitInput(Schema):
    name: str
    symbol: str
    definition: str
    unit_type: str


@router.post('', auth=jwt_auth)
def create_unit(request, data: CreateUnitInput):
    unit = Unit.objects.create(
        name=data.name,
        person=request.authenticated_user,
        symbol=data.symbol,
        definition=data.definition,
        unit_type=data.unit_type
    )
    return JsonResponse(unit_to_dict(unit))


@router.get('', auth=jwt_auth)
def get_units(request):
    units = Unit.objects.filter(Q(person=request.authenticated_user) | Q(person__isnull=True))
    return JsonResponse([unit_to_dict(unit) for unit in units], safe=False)


class UpdateUnitInput(Schema):
    name: str
    symbol: str
    definition: str
    unit_type: str


@router.patch('/{unit_id}', auth=jwt_auth)
def update_unit(request, unit_id: str, data: UpdateUnitInput):
    unit = Unit.objects.get(id=unit_id)
    if request.authenticated_user != unit.person:
        return JsonResponse({'detail': 'You are not authorized to update this unit.'}, status=403)

    if data.name is not None:
        unit.name = data.name
    if data.symbol is not None:
        unit.symbol = data.symbol
    if data.definition is not None:
        unit.definition = data.definition
    if data.unit_type is not None:
        unit.unit_type = data.unit_type

    unit.save()
    return JsonResponse(unit_to_dict(unit))


@router.delete('/{unit_id}', auth=jwt_auth)
def delete_unit(request, unit_id: str):
    try:
        unit = Unit.objects.get(id=unit_id)
    except Unit.DoesNotExist:
        return JsonResponse({'detail': 'Unit not found.'}, status=404)

    if request.authenticated_user != unit.person:
        return JsonResponse({'detail': 'You are not authorized to delete this unit.'}, status=403)

    unit.delete()
    return {'detail': 'Unit deleted successfully.'}
