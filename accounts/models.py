from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('livreur', 'Livreur'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')

    def __str__(self):
        return self.username

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/extra/')

    def __str__(self):
        return f"Image pour {self.product.name}"

from django.db import models
from django.contrib.auth import get_user_model

# Assuming CustomUser and Product models are defined elsewhere in your accounts/models.py
CustomUser = get_user_model()

class Order(models.Model):
    PAYMENT_CHOICES = (
        ('cash', 'Paiement en espèces'),
        ('card', 'Carte bancaire'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    client = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'client'},
        related_name='orders'
    )
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='orders'
    )
    quantity = models.PositiveIntegerField()
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_CHOICES
    )
    location = models.CharField(max_length=255)
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Computed total price (quantity * product.price)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Automatically compute total_price before saving if not set
        if not self.total_price:
            self.total_price = self.quantity * self.product.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Commande de {self.client.username} - {self.product.name}"

    class Meta:
        ordering = ['-created_at']  # Orders by most recent first
    
