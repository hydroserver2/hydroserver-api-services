from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.urls.exceptions import Http404
from sensorthings import models
from sensorthings.api.core.schemas import BasePostBody


class SensorThings:

    def __init__(self, host: str, path: str, entity: str):
        self.host = host
        self.path = path
        self.model = getattr(models, entity)

    def get_ref(self, entity_id: int) -> str:
        """
        Builds a reference URL for a given resource.

        :param entity_id: The id of the resource.
        :return: The resource's reference URL.
        """

        return f'{self.host}{self.path}({entity_id})'

    def list(self):
        pass

    def get(self):
        pass

    def create(self, entity_body, model=None) -> int:
        """"""

        active_model = model if model is not None else self.model
        entity_data = {}
        entity_links = {}

        for field, value in entity_body:
            nested_entity = entity_body.__fields__.get(field).field_info.extra.get(
                'nested_class', ''
            ).replace('PostBody', '')

            if issubclass(type(value), BasePostBody):
                entity_data[f'{field}_id'] = self.create(
                    entity_body=value,
                    model=getattr(models, nested_entity)
                )
            elif isinstance(value, list):
                entity_links[field] = [
                    self.create(
                        entity_body=sub_value,
                        model=getattr(models, nested_entity)
                    ) if issubclass(type(sub_value), BasePostBody) else sub_value.id for sub_value in value
                ]
            else:
                entity_data[field] = value

        db_entity = active_model(**entity_data)
        db_entity.save()

        for related_field, related_ids in entity_links.items():
            if related_ids:
                getattr(db_entity, related_field).add(*related_ids)

        return db_entity.id

    def update(self, entity_id, entity_body):
        """"""

        try:
            db_entity = self.model.objects.get(pk=entity_id)
        except ObjectDoesNotExist:
            raise Http404

        for attr, value in entity_body.dict(exclude_unset=True).items():
            setattr(db_entity, attr, value)

        db_entity.save()

        return entity_id

    def delete(self, entity_id):
        """"""

        try:
            db_entity = self.model.objects.get(pk=entity_id)
        except ObjectDoesNotExist:
            raise Http404

        db_entity.delete()


class SensorThingsRequest(HttpRequest):
    engine: SensorThings
