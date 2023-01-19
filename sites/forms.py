from sensorthings.models import Thing
from django.forms import ModelForm


class ThingForm(ModelForm):
    class Meta:
        model = Thing
        fields = ['name', 'description']
