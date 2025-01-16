from django import forms
from iam.schemas import ProfilePatchBody


class UserSignupForm(forms.Form):
    first_name = forms.CharField(max_length=30, required=False, label="firstName")
    middle_name = forms.CharField(max_length=30, required=False, label="middleName")
    last_name = forms.CharField(max_length=100, required=False, label="lastName")
    phone = forms.CharField(max_length=15, required=False)
    address = forms.CharField(max_length=255, required=False)
    link = forms.URLField(max_length=2000, required=False)
    user_type = forms.CharField(max_length=255, required=False, label="type")
    organization = forms.JSONField(required=False)

    def __init__(self, *args, **kwargs):
        if "data" in kwargs:
            data = kwargs["data"].copy()
            for field_name, field in self.base_fields.items():
                alias = field.label or field_name
                if alias in data:
                    data[field_name] = data.pop(alias)
            kwargs["data"] = data
        super().__init__(*args, **kwargs)

    def signup(self, request, user):
        profile = ProfilePatchBody(**self.cleaned_data)
        profile.save(user)
