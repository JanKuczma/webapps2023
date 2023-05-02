from django.db import models
from django.contrib.auth.models import User


User._meta.get_field('email')._unique = True


currency_choices = (
    ('GBP', 'Pounds'),
    ('USD', 'US Dollars'),
    ('EUR', 'Euros'),
)


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, choices=currency_choices, default='GBP')

    def __str__(self):
        return f"{self.user.username}'s account"
