import decimal

from django.http import JsonResponse
from .currency_converter import convert_currency, rates as exchange_rates


def conversion(request, currency1, currency2, amount):
    try:
        decimal.Decimal(amount)
    except ValueError:
        return JsonResponse({'error': 'Could not convert amount to a decimal number'}, status=400)
    try:
        # Retrieve exchange rate from dictionary
        exchange_rate = exchange_rates[currency1][currency2]
        # Perform conversion
        converted_amount = convert_currency(currency1, currency2, decimal.Decimal(amount))

        # Return result in JSON format
        return JsonResponse({'conversion_rate': exchange_rate, 'converted_amount': converted_amount})

    except KeyError:
        # Handle unsupported currency
        return JsonResponse({'error': 'One or both of the provided currencies are not supported'}, status=400)
