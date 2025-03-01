from django.urls import path
from .views import create_payment_intent, stripe_webhook, save_payment_method

app_name = 'payment'  # Namespace for the app

urlpatterns = [
    path('create-payment-intent/', create_payment_intent, name='create_payment_intent'),
    path('stripe-webhook/', stripe_webhook, name='stripe_webhook'),
    path('save-payment-method/', save_payment_method, name='save_payment_method'),
]