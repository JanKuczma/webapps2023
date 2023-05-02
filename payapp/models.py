from django.db import models
from django.contrib.auth.models import User


User._meta.get_field('email')._unique = True


status_choices = (
    ('P', 'Pending'),
    ('A', 'Accepted'),
    ('R', 'Rejected'),
)


class Transaction(models.Model):
    from_account = models.ForeignKey(User, related_name='from_account', on_delete=models.CASCADE)
    to_account = models.ForeignKey(User, related_name='to_account', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    conversion_rate = models.DecimalField(max_digits=10, decimal_places=2, default=1.0)
    date = models.DateTimeField(auto_now_add=True)


class PaymentRequest(models.Model):
    from_account = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_payment_requests')
    to_account = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_payment_requests')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=status_choices, default='P')
    transaction = models.ForeignKey(Transaction, related_name='transaction', on_delete=models.DO_NOTHING, null=True, default=None)
