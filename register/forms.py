from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from register.models import currency_choices, User


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    currency = forms.ChoiceField(choices=currency_choices)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
