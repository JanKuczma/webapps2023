from django import forms
from register.models import Account
from django.db.models import Q


class TransferForm(forms.Form):
    account = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'placeholder': 'Username or Email'}))
    amount = forms.DecimalField(max_digits=10, decimal_places=2)

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount

    def clean_account(self):
        account = self.cleaned_data['account']
        try:
            Account.objects.get(Q(user__username=account) | Q(user__email=account))
        except Account.DoesNotExist:
            raise forms.ValidationError("Recipient account does not exist.")
        return account
