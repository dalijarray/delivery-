from django.urls import path
from . import views

urlpatterns = [
    path('process/<int:product_id>/', views.process_payment, name='process_payment'),
    path('success/<int:payment_id>/', views.payment_success, name='payment_success'),
]