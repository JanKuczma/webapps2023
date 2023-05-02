import decimal
from django.db.models.signals import post_migrate
from register.models import User, Account
from django.dispatch import receiver


@receiver(post_migrate)
def create_admin_user(sender, **kwargs):
    if sender.name == 'payapp':
        if not User.objects.filter(username='admin1').exists():
            user = User.objects.create_superuser('admin1', 'admin1@example.com', 'admin1')
            Account.objects.create(user=user, balance=decimal.Decimal('1000.00'), currency='GBP')
