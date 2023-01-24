from sensorthings.models import Thing
from django.forms import ModelForm, FloatField


class ThingForm(ModelForm):
    latitude = FloatField(required=True)
    longitude = FloatField(required=True)
    elevation = FloatField(required=True)

    class Meta:
        model = Thing
        fields = ['name', 'description', 'latitude', 'longitude', 'elevation']


