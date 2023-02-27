from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

from .models import CustomUser


class SignUpForm(UserCreationForm):
    middle_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    phone = forms.CharField(max_length=15, required=False, help_text='Optional.')
    address = forms.CharField(max_length=255, required=False, help_text='Optional.')

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2', 'middle_name', 'phone', 'address')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with that email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        if commit:
            user.save()
        return user


class UpdateAccountForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'middle_name', 'phone', 'address', 'organization')

    def __init__(self, *args, **kwargs):
        super(UpdateAccountForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        self.fields['middle_name'].required = False
        self.fields['phone'].required = False
        self.fields['phone'].validators.append(
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        )
        self.fields['address'].required = False
        self.fields['organization'].required = False
        if instance:
            self.fields['first_name'].initial = instance.first_name
            self.fields['first_name'].initial = instance.first_name
            self.fields['last_name'].initial = instance.last_name
            self.fields['middle_name'].initial = instance.middle_name
            self.fields['phone'].initial = instance.phone
            self.fields['address'].initial = instance.address
            self.fields['organization'].initial = instance.organization

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and get_user_model().objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email is already in use by another user.")
        return email
