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

class Order(models.Model):
    PAYMENT_CHOICES = (
        ('cash', 'Paiement en espèces'),
        ('card', 'Carte bancaire'),
    )
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'client'})
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')

    def total_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"Commande de {self.client.username} - {self.product.name}"