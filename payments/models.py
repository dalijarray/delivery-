from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import Product

class Payment(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    card_number = models.CharField(max_length=16)
    card_expiry = models.CharField(max_length=5)  # MM/YY format
    card_cvc = models.CharField(max_length=4)
    status = models.CharField(max_length=20, default='pending')  # e.g., pending, success, failed
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} by {self.user.username}"