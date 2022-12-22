from .models import Site
from django.forms import ModelForm
from django import forms


class SiteForm(ModelForm):
    class Meta:
        model = Site
        fields = ['name', 'latitude', 'longitude', 'elevation']
        # widgets = {
        #     'name': forms.CheckboxSelectMultiple(),
        # }
