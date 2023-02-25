from ninja import Schema, Field
from hydrothings import components as st_components


class ThingProperties(Schema):
    sampling_feature_type: str = Field(..., alias='samplingFeatureType')
    sampling_feature_code: str = Field(..., alias='samplingFeatureCode')


class ThingGetResponse(st_components.ThingGetResponse):
    properties: ThingProperties
