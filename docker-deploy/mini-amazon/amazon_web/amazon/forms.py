from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import *
from django_countries.fields import CountryField


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = AmazonUser
        fields = ("username", "email", "password1", "password2")


class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=16)
    password = forms.CharField(label=("Password"), widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': ("Please enter a correct %(username)s and password. "),
        'inactive': ("This account is not registered, please register first."),
    }

class OrderInfoForm(forms.Form):
    city = forms.CharField(label=_("City"), max_length=100, required=True)
    state = forms.CharField(label=_("State"), max_length=200, required=True)
    country = CountryField().formfield()
    address_x = forms.IntegerField()
    address_y = forms.IntegerField()

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = AmazonUser
        fields = ("username", "email", "ups_account")

