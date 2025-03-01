import stripe
import logging
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import PaymentMethod, PaymentType
logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def create_payment_intent(request):
    if request.method == 'POST':
        try:
            # Get payment details from the request
            amount = int(request.POST.get('amount', 0))  # Already in cents
            currency = request.POST.get('currency', 'usd').lower()
            product_id = request.POST.get('product_id')
            quantity = int(request.POST.get('quantity', 1))

            # Validate minimum amount based on currency (example for USD)
            if currency == 'usd' and amount < 50:
                return JsonResponse({'error': 'Amount must be at least $0.50 for USD'}, status=400)

            # Create a PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                payment_method_types=['card'],
            )

            return JsonResponse({
                'clientSecret': intent['client_secret'],
                'product_id': product_id,
                'quantity': quantity,
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    try:
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            logger.info(f"PaymentIntent {payment_intent['id']} succeeded: {payment_intent}")
            
            # Check if payment_method exists and is valid
            payment_method_id = payment_intent.get('payment_method')
            if payment_method_id:
                try:
                    # Use stripe_payment_method_id to query the PaymentMethod
                    payment_method = PaymentMethod.objects.get(stripe_payment_method_id=payment_method_id)
                    payment_method.details = f"Transaction ID: {payment_intent['id']}"
                    payment_method.save()
                    logger.info(f"Updated PaymentMethod {payment_method.id} with transaction {payment_intent['id']}")
                except PaymentMethod.DoesNotExist:
                    logger.warning(f"PaymentMethod not found for stripe_payment_method_id: {payment_method_id}")
                    # Optionally, create a new PaymentMethod or skip silently
                    return JsonResponse({'status': 'success', 'warning': f'PaymentMethod not found for {payment_method_id}, skipped update'}, status=200)
                except Exception as e:
                    logger.error(f"Error updating PaymentMethod: {str(e)}")
                    return JsonResponse({'error': f"Failed to update PaymentMethod: {str(e)}"}, status=500)
            else:
                logger.warning("No payment_method found in payment_intent.succeeded event")
                return JsonResponse({'status': 'success', 'warning': 'No payment_method in event, skipped update'}, status=200)

        elif event['type'] == 'payment_intent.failed':
            payment_intent = event['data']['object']
            logger.info(f"PaymentIntent {payment_intent['id']} failed: {payment_intent.get('last_payment_error', {}).get('message', 'No error message')}")
            return JsonResponse({'status': 'success'})

        else:
            logger.info(f"Unhandled event type: {event['type']}")
            return JsonResponse({'status': 'success', 'message': f'Unhandled event type: {event["type"]}'}, status=200)

        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error(f"Unexpected error in webhook: {str(e)}")
        return JsonResponse({'error': f"Internal server error: {str(e)}"}, status=500)

def save_payment_method(request):
    if request.method == 'POST':
        try:
            payment_type = PaymentType.objects.get(name='CREDIT_CARD')  # Adjust for cash if needed
            stripe_payment_method_id = request.POST.get('card_details', '')  # Get Stripe payment method ID
            
            # Check if a PaymentMethod already exists for this Stripe payment method ID
            payment_method, created = PaymentMethod.objects.get_or_create(
                stripe_payment_method_id=stripe_payment_method_id,
                defaults={
                    'type': payment_type,
                    'details': f"Stripe Payment Method: {stripe_payment_method_id}",
                    'is_default': True,
                }
            )
            
            if not created:
                payment_method.details = f"Stripe Payment Method: {stripe_payment_method_id}"
                payment_method.save()
            
            return JsonResponse({'status': 'success', 'payment_method_id': payment_method.id})
        except PaymentType.DoesNotExist:
            return JsonResponse({'error': 'Payment type not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)