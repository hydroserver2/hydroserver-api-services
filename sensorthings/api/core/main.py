import json
import pandas as pd
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.urls.exceptions import Http404
from pydantic.fields import SHAPE_LIST
from pydantic import BaseModel
from sensorthings import models
from sensorthings.api.core.schemas import BasePostBody
from sensorthings.api import components as component_schemas
from django.conf import settings


class SensorThings:

    def __init__(self, host: str, scheme: str, path: str, component: str):
        self.host = host
        self.scheme = scheme
        self.path = path
        self.model = getattr(models, component)

    def get_ref(self, entity_id: int | None = None, related_component: str | None = None) -> str:
        """
        Builds a reference URL for a given resource.

        :param entity_id: The id of the resource.
        :param related_component: The related component to be appended to the ref URL.
        :return: The resource's reference URL.
        """

        ref_url = f'{self.scheme}://{self.host}{self.path}'

        if entity_id is not None:
            ref_url = f'{ref_url}({entity_id})'

        if related_component is not None:
            ref_url = f'{ref_url}/{related_component}'

        return ref_url

    def list(self, filter, count, order_by, skip, top, select, expand, result_format):
        """"""

        query = self.model.objects
        response = {}

        if filter is not None:
            query = self.apply_filters(query, filter)

        response_count = self.get_count(query)

        if order_by is not None:
            query = self.apply_order(query, order_by)

        if select is not None:
            query = self.apply_select(query, select)

        if expand is not None:
            query = self.apply_expand(query, expand)

        if count is True:
            response['count'] = response_count

        queryset = query.values()

        if top is not None or skip != 0:
            queryset = self.apply_pagination(queryset, top, skip)

        response_df = pd.DataFrame(list(queryset))

        response_df = self.deserialize_json_fields(response_df)
        response_df = self.build_related_links(response_df)
        response_df = self.build_self_links(response_df)

        response['value'] = response_df.to_dict('records')

        if top is not None and (top + skip) < response_count:
            response['next_link'] = self.build_next_link(top, skip)

        return response

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
            elif issubclass(type(value), BaseModel):
                entity_data[field] = json.dumps(value.dict())
            elif isinstance(value, dict):
                entity_data[field] = json.dumps(value)
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

    def apply_filters(self, query, filters):
        """"""

        # TODO

        return query

    def get_count(self, query):
        """
        Returns a count of the objects that would be returned by the given query.

        :param query: The query object to be counted.
        :return count: A count of the objects in the resulting queryset.
        """

        return query.count()

    def apply_order(self, query, order_by):
        """"""

        # TODO

        return query

    def apply_pagination(self, queryset, top, skip):
        """"""

        if top is not None:
            queryset = queryset[skip:skip+top]
        else:
            queryset = queryset[skip:]

        return queryset

    def apply_select(self, query, select):
        """"""

        # TODO

        return query

    def apply_expand(self, query, expand):
        """"""

        # TODO

        return query

    def build_next_link(self, top, skip):
        """"""

        return f'{self.get_ref()}?$top={top}&$skip={top+skip}'

    def deserialize_json_fields(self, response_df):
        """"""

        for name, field in getattr(component_schemas, f'{self.model.__name__}Fields').__fields__.items():
            if field.type_ == dict and not response_df.empty:
                response_df[name] = response_df.apply(
                    lambda row: json.loads(getattr(row, name)) if getattr(row, name) is not None else None,
                    axis=1
                )
            elif isinstance(field, BaseModel) and not response_df.empty:
                response_df[name] = response_df.apply(
                    lambda row: json.loads(getattr(row, name).dict()) if getattr(row, name) is not None else None,
                    axis=1
                )

        return response_df

    def build_related_links(self, response_df):
        """"""

        for name, field in getattr(component_schemas, f'{self.model.__name__}Relations').__fields__.items():
            if not response_df.empty:
                if field.shape == SHAPE_LIST:
                    related_component = [
                        component for component
                        in settings.ST_CAPABILITIES
                        if component['SINGULAR_NAME'] == field.type_.__name__
                    ][0]['NAME']
                else:
                    related_component = field.type_.__name__

                response_df[f'{name}_link'] = response_df.apply(
                    lambda row: self.get_ref(row.id, related_component),
                    axis=1
                )

        return response_df

    def build_self_links(self, response_df):
        """"""

        if not response_df.empty:
            response_df['self_link'] = response_df.apply(
                lambda row: self.get_ref(row.id),
                axis=1
            )

        return response_df


class SensorThingsRequest(HttpRequest):
    engine: SensorThings
