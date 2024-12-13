from django import forms
from allauth.account.forms import SignupForm
from .models import Person, PersonType


class HydroServerSignUpForm(SignupForm):
    first_name = forms.CharField(
        label='First Name',
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )

    middle_name = forms.CharField(
        label='Middle Name',
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Middle Name'})
    )

    last_name = forms.CharField(
        label='Last Name',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )

    address = forms.CharField(
        label='Address',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Address'})
    )

    phone = forms.CharField(
        label='Phone Number',
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Phone Number',
            'class': 'phone-number-mask'
        })
    )

    type = forms.ModelChoiceField(
        label='Type',
        queryset=PersonType.objects.all(),
        required=True,
    )

    class Meta:
        model = Person

    def save(self, request):
        person = super(HydroServerSignUpForm, self).save(request)
        person.middle_name = str(self.cleaned_data.get('middle_name'))
        person.phone = str(self.cleaned_data.get('phone'))
        person.address = str(self.cleaned_data.get('address'))
        person.type = str(self.cleaned_data.get('type'))
        person.save()

        return person
