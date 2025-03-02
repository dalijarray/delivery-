from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Payment
from accounts.models import Product
from django.contrib import messages
from datetime import datetime
import re
from accounts.models import Order
def luhn_checksum(card_number):
    """Validate a card number using the Luhn algorithm."""
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10 == 0

@login_required
def process_payment(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        card_number = request.POST.get('card_number')
        card_expiry = request.POST.get('card_expiry')
        card_cvc = request.POST.get('card_cvc')
        quantity = int(request.POST.get('quantity', 1))

        # Basic validation (mocked for demo purposes)
        if not (card_number and card_expiry and card_cvc):
            messages.error(request, "All card details are required.")
            return render(request, 'payments/payment_form.html', {'product': product})

        if len(card_number) != 16 or not card_number.isdigit():
            messages.error(request, "Invalid card number. Must be 16 digits.")
            return render(request, 'payments/payment_form.html', {'product': product})

        if len(card_cvc) not in [3, 4] or not card_cvc.isdigit():
            messages.error(request, "Invalid CVC. Must be 3 or 4 digits.")
            return render(request, 'payments/payment_form.html', {'product': product})

        # Mocked payment processing
        amount = product.price * quantity
        payment = Payment.objects.create(
            user=request.user,
            product=product,
            amount=amount,
            card_number=card_number[-4:],
            card_expiry=card_expiry,
            card_cvc='***',
            status='success'
        )

        # Save the order
        order = Order(
            client=request.user,
            product=product,
            quantity=quantity,
            payment_method='card',
            total_price=amount,
            status='pending'
        )
        order.save()

        # Update product stock
        product.stock -= quantity
        product.save()

        # Redirect to orders page
        return redirect('orders')

    return render(request, 'payments/payment_form.html', {'product': product})

@login_required
def payment_success(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    return render(request, 'payments/success.html', {'payment': payment})

@login_required
def orders(request):
    if request.user.role != 'client':
        return redirect('login')

    orders = Order.objects.filter(client=request.user).order_by('-created_at')
    return render(request, 'accounts/orders.html', {'orders': orders})