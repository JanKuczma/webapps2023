from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import UserRegisterForm
from .models import Account
from django.contrib.auth.forms import AuthenticationForm
import json
import requests
from django.contrib import messages


def home(request):
    return redirect('login')


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
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
                acc = Account(user=user, balance=balance, currency=currency)
                acc.save()

                # Show success message and redirect to login page
                username = form.cleaned_data.get('username')
                messages.success(request, f'Account created for {username}!')
                return redirect('login')
            else:
                messages.error(request, 'Currency conversion API error')
        else:
            messages.error(request, 'Form validation error')
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


def login_user(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = AuthenticationForm(data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'You have been logged in successfully')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'users/login.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('login')