from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('transfer/', views.transfer, name='transfer'),
    path('request/', views.request_payment, name='request'),
    path('payment/', views.make_payment, name='payment'),
    path('reject/', views.reject, name='reject'),
]
