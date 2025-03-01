from django.db import models

class PaymentType(models.Model):
    """
    Represents the type of payment (e.g., CREDIT_CARD, CASH_ON_DELIVERY).
    """
    name = models.CharField(max_length=50, choices=[
        ('CREDIT_CARD', 'Credit Card'),
        ('CASH_ON_DELIVERY', 'Cash on Delivery'),
    ], unique=True)

    def __str__(self):
        return self.name

class PaymentMethod(models.Model):
    """
    Represents a payment method with a type and additional details.
    """
    type = models.ForeignKey(PaymentType, on_delete=models.CASCADE, related_name='payment_methods')
    stripe_payment_method_id = models.CharField(max_length=255, unique=True, null=True, blank=True)  # Store Stripe payment method ID
    details = models.CharField(max_length=255, blank=True, null=True)  # Optional details like card number, etc.
    is_default = models.BooleanField(default=False)  # Indicates if this is the default payment method

    def __str__(self):
        return f"{self.type.name} - {'Default' if self.is_default else 'Not Default'}"