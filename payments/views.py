from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from decouple import config
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import paypalrestsdk
from payments.models import Payment
from payments.serializers.common import PaymentSerializer
from items.models import Item

# Configure PayPal SDK
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})


@csrf_exempt
@require_http_methods(["POST"])
def get_access_token(request):
    url = f"https://api.{settings.PAYPAL_MODE}.paypal.com/v1/oauth2/token"
    headers = {"Accept": "application/json", "Accept-Language": "en_US"}
    data = {"grant_type": "client_credentials"}
    auth = (settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET)
    response = requests.post(url, headers=headers, data=data, auth=auth)
    return JsonResponse({"access_token": response.json()["access_token"]})


@csrf_exempt
@require_http_methods(["POST"])
def create_order(request):
    access_token = get_access_token(request).content.decode()[
        "access_token"]  # Fetch token
    url = f"https://api.{settings.PAYPAL_MODE}.paypal.com/v2/checkout/orders"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    # Example payload: Adjust for your app (e.g., dynamic amount from cart)
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "USD",
                "value": "10.00"  # Test amount
            },
            "description": "Test Product"
        }]
    }
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    if response.status_code == 201:
        return JsonResponse({"id": data["id"], "links": data["links"]})
    return JsonResponse({"error": data}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def capture_order(request):
    order_id = request.POST.get("orderID")
    payer_id = request.POST.get("payerID")  # From frontend approval
    access_token = get_access_token(request).content.decode()["access_token"]
    url = f"https://api.{settings.PAYPAL_MODE}.paypal.com/v2/checkout/orders/{order_id}/capture"
    headers = {"Content-Type": "application/json",
               "Authorization": f"Bearer {access_token}"}
    response = requests.post(url, headers=headers)
    data = response.json()
    if response.status_code == 201:
        # Save to DB: e.g., mark order as paid
        return JsonResponse({"status": "success", "details": data})
    return JsonResponse({"error": data}, status=400)


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        item_id = request.data.get('item_id')
        shipping_address = request.data.get('shipping_address')

        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return Response(
                {"error": "Item not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Create PayPal payment
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": f"{settings.FRONTEND_URL}/payment/success",
                "cancel_url": f"{settings.FRONTEND_URL}/payment/cancel"
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": item.item_name,
                        "sku": str(item.id),
                        "price": str(item.current_bid),
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": str(item.current_bid),
                    "currency": "USD"
                },
                "description": f"Purchase of {item.item_name}"
            }]
        })

        if payment.create():
            # Save payment record
            Payment.objects.create(
                user=request.user,
                item=item,
                paypal_order_id=payment.id,
                amount=item.current_bid,
                shipping_address=shipping_address,
                status='pending'
            )

            # Find approval URL
            approval_url = next(
                (link.href for link in payment.links if link.rel == "approval_url"),
                None
            )

            return Response({
                "order_id": payment.id,
                "approval_url": approval_url
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"error": payment.error},
                status=status.HTTP_400_BAD_REQUEST
            )


class CaptureOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('order_id')
        payer_id = request.data.get('payer_id')

        try:
            payment_record = Payment.objects.get(paypal_order_id=order_id)
        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        payment = paypalrestsdk.Payment.find(order_id)

        if payment.execute({"payer_id": payer_id}):
            # Update payment status
            payment_record.status = 'completed'
            payment_record.save()

            # Update item
            item = payment_record.item
            item.highest_bidder = request.user
            item.payment_confirmation = True
            item.save()

            return Response({
                "message": "Payment completed successfully",
                "payment": PaymentSerializer(payment_record).data
            }, status=status.HTTP_200_OK)
        else:
            payment_record.status = 'failed'
            payment_record.save()
            return Response(
                {"error": payment.error},
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payments = Payment.objects.filter(user=request.user)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
