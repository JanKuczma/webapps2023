from django.urls import path
from . import views
urlpatterns = [
    path('accounts/', views.admin_accounts, name='admin_accounts'),
    path('register/', views.register_admin, name='register_admin'),
    path('transactions/', views.admin_transactions_view, name='admin_transactions_view')
]