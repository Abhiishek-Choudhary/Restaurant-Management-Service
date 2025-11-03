import razorpay
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from orders.models import Order
from .models import Payment
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import hmac, hashlib, json
from razorpay.errors import SignatureVerificationError
from .models import Payment

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_order(request):
    user = request.user
    order_id = request.data.get("order_id")

    if not order_id:
        return Response({"error": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    order = get_object_or_404(Order, id=order_id, user=user)

    if order.payment_status.lower() != "pending":
        return Response(
            {"error": f"Payment already {order.payment_status.lower()} for this order."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        razorpay_order = client.order.create({
            "amount": int(order.total * 100),  # convert to paise
            "currency": "INR",
            "payment_capture": 1
        })

        payment = Payment.objects.create(
            user=user,
            order=order,
            razorpay_order_id=razorpay_order["id"],
            amount=order.total,
            status="PENDING"
        )

        order.payment_status = "PROCESSING"
        order.save()

        return Response({
            "status": "success",
            "message": "Payment order created successfully",
            "order_id": razorpay_order["id"],
            "amount": order.total,
            "currency": "INR",
            "key": settings.RAZORPAY_KEY_ID
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_payment(request):
    data = request.data
    order_id = data.get("razorpay_order_id")
    payment_id = data.get("razorpay_payment_id")
    signature = data.get("razorpay_signature")

    if not all([order_id, payment_id, signature]):
        return Response({"error": "Missing payment verification details"}, status=status.HTTP_400_BAD_REQUEST)

    payment = get_object_or_404(Payment, razorpay_order_id=order_id)

    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })

        payment.razorpay_payment_id = payment_id
        payment.razorpay_signature = signature
        payment.status = "SUCCESS"
        payment.save()

        order = payment.order
        order.payment_status = "PAID"
        order.save()

        return Response({"status": "success", "message": "Payment verified successfully"}, status=status.HTTP_200_OK)

    except razorpay.errors.SignatureVerificationError:
        payment.status = "FAILED"
        payment.save()
        return Response({"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        payment.status = "FAILED"
        payment.save()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
def razorpay_webhook(request):
    webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
    received_data = request.body.decode()
    received_signature = request.headers.get("X-Razorpay-Signature")

    # Validate signature
    generated_signature = hmac.new(
        webhook_secret.encode(),
        received_data.encode(),
        hashlib.sha256
    ).hexdigest()

    if generated_signature != received_signature:
        return JsonResponse({"status": "invalid signature"}, status=400)

    data = json.loads(received_data)

    if data.get("event") == "payment.captured":
        rp_order_id = data["payload"]["payment"]["entity"]["order_id"]
        rp_payment_id = data["payload"]["payment"]["entity"]["id"]

        try:
            payment = Payment.objects.get(razorpay_order_id=rp_order_id)
            payment.status = "paid"
            payment.razorpay_payment_id = rp_payment_id
            payment.save()

            order = payment.order
            order.payment_status = "paid"
            order.save()

        except Payment.DoesNotExist:
            pass

    return JsonResponse({"status": "success"})
