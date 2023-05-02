from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import TransferForm
from register.models import Account
from .models import Transaction, PaymentRequest
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q
from django.db import transaction
import json
import requests
import decimal
from django.contrib import messages


@login_required
def profile(request):
    form = PasswordChangeForm(user=request.user, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            messages.success(request, 'Password changed successfully. Log in in with your new password.')
            form.save()
            return redirect('logout')
        else:
            messages.error(request, 'Form validation error')
    return render(request, 'users/profile.html', {'form': form})


@login_required
def dashboard(request):
    payment_requests = PaymentRequest.objects.filter(Q(from_account=request.user) | Q(to_account=request.user)).order_by('-date')
    transactions = Transaction.objects.filter(Q(from_account=request.user) | Q(to_account=request.user)).order_by('-date')
    return render(request, 'payapp/dashboard.html', {'payment_requests': payment_requests, 'transactions': transactions})


@login_required
@transaction.atomic
def transfer(request):
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            recipient = form.cleaned_data['account']
            sender_account = Account.objects.select_for_update().get(user=request.user)
            recipient_account = Account.objects.select_for_update().get(Q(user__username=recipient) | Q(user__email=recipient))
            if recipient_account.user != request.user:
                # Build the URL for the currency conversion API
                url = request.build_absolute_uri(f'/webapps2023/conversion/{sender_account.currency}/{recipient_account.currency}/{amount}/')
                # Call the API to get the exchange rate
                response = requests.get(url)
                if response.status_code == 200:
                    # Parse the response JSON to get the converted amount
                    data = json.loads(response.text)
                    converted_amount = decimal.Decimal(data['converted_amount'])
                    if sender_account.balance >= amount:
                        sender_account.balance -= amount
                        recipient_account.balance += converted_amount
                        messages.success(request, f'''
                        Transfer successful. You transferred 
                        {amount}{sender_account.currency} to {recipient}.
                        {recipient} got {converted_amount}{recipient_account.currency}.
                        Conversion rate: {data['conversion_rate']}.
                        ''')
                        Transaction(from_account=sender_account.user, to_account=recipient_account.user, amount=amount, conversion_rate=data['conversion_rate']).save()
                        sender_account.save()
                        recipient_account.save()
                        return redirect('dashboard')
                    else:
                        messages.error(request, 'Transfer failed. You do not have sufficient funds in your account.')
                else:
                    messages.error(request, 'Currency conversion API error')
            else:
                messages.error(request, 'Cannot send money yourself.')
        else:
            messages.error(request, 'Form validation error')

    else:
        form = TransferForm()
    return render(request, 'payapp/transfer.html', {'form': form})


@login_required
def request_payment(request):
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            account = form.cleaned_data['account']
            to_account = Account.objects.select_for_update().get(user=request.user)
            from_account = Account.objects.select_for_update().get(Q(user__username=account) | Q(user__email=account))
            if from_account.user != request.user:
                # Parse the response JSON to get the converted amount
                messages.success(request, f'''
                        Request successful. You requested 
                        {amount}{to_account.currency} from {from_account}.
                        ''')
                PaymentRequest(from_account=from_account.user, to_account=to_account.user, amount=amount).save()
                return redirect('dashboard')
            else:
                messages.error(request, 'Cannot request money from yourself.')
        else:
            messages.error(request, 'Form validation error')
    else:
        form = TransferForm()
    return render(request, 'payapp/request_payment.html', {'form': form})


@login_required
@transaction.atomic
def make_payment(request):
    if request.method == 'POST':
        payment_id = request.POST.get("payment_request", "")
        try:
            payment_request = PaymentRequest.objects.select_for_update().get(id=payment_id)
        except PaymentRequest.DoesNotExist:
            messages.error(request, 'Payment request not found.')
        if payment_request.from_account == request.user:
            if payment_request.status == 'P':
                amount = payment_request.amount
                recipient = payment_request.to_account
                sender_account = Account.objects.select_for_update().get(user=request.user)
                recipient_account = recipient.account
                # Build the URL for the currency conversion API
                url = request.build_absolute_uri(f'/webapps2023/conversion/{sender_account.currency}/{recipient_account.currency}/{0}/')
                # Call the API to get the exchange rate
                response = requests.get(url)
                if response.status_code == 200:
                    # Parse the response JSON to get the converted amount
                    data = json.loads(response.text)
                    rate = decimal.Decimal('1.0') / decimal.Decimal(data['conversion_rate'])
                    converted_amount = round(rate * amount, 2)
                    if sender_account.balance >= converted_amount:
                        sender_account.balance -= converted_amount
                        recipient_account.balance += amount
                        payment_request.status = 'A'
                        messages.success(request, 'Payment Request Accepted.')
                        messages.success(request, f'''
                        Transfer successful. You transferred 
                        {round(converted_amount,2)}{sender_account.currency} to {recipient}.
                        {recipient} got {amount}{recipient_account.currency}.
                        Conversion rate: {decimal.Decimal(data['conversion_rate'])}.
                        ''')
                        tx = Transaction(from_account=sender_account.user, to_account=recipient_account.user, amount=converted_amount, conversion_rate=decimal.Decimal(data['conversion_rate']))
                        payment_request.transaction = tx
                        tx.save()
                        payment_request.save()
                        sender_account.save()
                        recipient_account.save()
                        return redirect('dashboard')
                    else:
                        messages.error(request, 'Transfer failed. You do not have sufficient funds in your account.')
                else:
                    messages.error(request, 'Currency conversion API error')
                    return redirect('dashboard')
            else:
                messages.error(request, 'Payment Request is not pending.')
        else:
            messages.error(request, 'Access denied.')
    return redirect('dashboard')


@login_required
def reject(request):
    if request.method == 'POST':
        payment_id = request.POST.get("payment_request", "")
        try:
            payment_request = PaymentRequest.objects.select_for_update().get(id=payment_id)
        except PaymentRequest.DoesNotExist:
            messages.error(request, 'Payment request not found.')
        if payment_request.from_account == request.user:
            if payment_request.status == 'P':
                payment_request.status = 'R'
                messages.success(request, 'Payment Request rejected.')
                payment_request.save()
                return redirect('dashboard')
            else:
                messages.error(request, 'Payment Request is not pending.')
        else:
            messages.error(request, 'Access denied.')
    return redirect('dashboard')
