from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from payapp.models import Transaction, PaymentRequest
from register.models import Account
from register.forms import UserRegisterForm
import json
import requests
from django.contrib import messages


@staff_member_required
@login_required
def admin_accounts(request):
    accounts = Account.objects.all()
    return render(request, 'admin/admin_accounts.html', {'accounts': accounts})


@staff_member_required
@login_required
def register_admin(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # Get the selected currency from the form
            currency = form.cleaned_data['currency']

            # Build the URL for the currency conversion API
            url = request.build_absolute_uri(f'/webapps2023/conversion/GBP/{currency}/1000/')

            # Call the API to get the exchange rate
            response = requests.get(url)
            if response.status_code == 200:
                # Parse the response JSON to get the converted amount
                data = json.loads(response.text)
                balance = data['converted_amount']

                # Create the user account with the converted balance and currency
                user = form.save()
                user.is_staff = True
                user.is_superuser = True
                user.save()
                acc = Account(user=user, balance=balance, currency=currency)
                acc.save()

                # Show success message and redirect to login page
                username = form.cleaned_data.get('username')
                messages.success(request, f'Account created for {username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Currency conversion API error')
        else:
            messages.error(request, 'Form validation error')
    else:
        form = UserRegisterForm()

    return render(request, 'admin/register_admin.html', {'form': form})


@staff_member_required
@login_required
def admin_transactions_view(request):
    transactions = Transaction.objects.all()
    payment_requests = PaymentRequest.objects.all()
    return render(request, 'payapp/dashboard.html', {'payment_requests': payment_requests, 'transactions': transactions})
