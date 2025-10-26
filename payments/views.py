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
from .serializers.common import PaymentSerializer
import requests
import base64
from payments.models import Payment
from items.models import Item
import logging

logger = logging.getLogger(__name__)


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get_access_token(self):
        """Get PayPal OAuth token"""
        try:
            url = f"{settings.PAYPAL_API_BASE_URL}/v1/oauth2/token"
            auth = base64.b64encode(
                f"{settings.PAYPAL_CLIENT_ID}:{settings.PAYPAL_CLIENT_SECRET}".encode()
            ).decode()

            headers = {
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            data = {"grant_type": "client_credentials"}
            response = requests.post(
                url, headers=headers, data=data, timeout=10)
            response.raise_for_status()
            return response.json().get("access_token")
        except Exception as e:
            logger.error(f"Failed to get PayPal access token: {str(e)}")
            raise

    def post(self, request):
        item_id = request.data.get('item_id')
        shipping_address = request.data.get('shipping_address', {})

        if not item_id:
            return Response(
                {"error": "item_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return Response(
                {"error": "Item not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            # Get PayPal access token
            access_token = self.get_access_token()

            # Create PayPal order
            url = f"{settings.PAYPAL_API_BASE_URL}/v2/checkout/orders"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }

            # Ensure current_bid is valid
            amount = str(float(item.current_bid))

            # Get description - use getattr to safely access the field
            description = getattr(item, 'description', None) or getattr(
                item, 'item_desc', None) or "Item"

            payload = {
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": "USD",
                        "value": amount,
                        "breakdown": {
                            "item_total": {
                                "currency_code": "USD",
                                "value": amount
                            }
                        }
                    },
                    "items": [{
                        "name": item.item_name[:127],  # PayPal limit
                        "unit_amount": {
                            "currency_code": "USD",
                            "value": amount
                        },
                        "quantity": "1",
                        "description": description[:127] if description else "Item",
                        "sku": str(item.id),
                        "category": "PHYSICAL_GOODS"
                    }]
                }]
            }

            logger.info(f"Creating PayPal order with payload: {payload}")
            response = requests.post(
                url, json=payload, headers=headers, timeout=10)
            order_data = response.json()

            if response.status_code == 201:
                # Save payment record
                Payment.objects.create(
                    user=request.user,
                    item=item,
                    paypal_order_id=order_data['id'],
                    amount=item.current_bid,
                    shipping_address=shipping_address,
                    status='pending'
                )

                return Response({
                    "order_id": order_data['id']
                }, status=status.HTTP_201_CREATED)
            else:
                logger.error(f"PayPal order creation failed: {order_data}")
                return Response(
                    {"error": order_data.get(
                        'message', 'Failed to create order'), "details": order_data},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            logger.error(
                f"Error creating PayPal order: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Internal server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CaptureOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get_access_token(self):
        """Get PayPal OAuth token"""
        try:
            url = f"{settings.PAYPAL_API_BASE_URL}/v1/oauth2/token"
            auth = base64.b64encode(
                f"{settings.PAYPAL_CLIENT_ID}:{settings.PAYPAL_CLIENT_SECRET}".encode()
            ).decode()

            headers = {
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            data = {"grant_type": "client_credentials"}
            response = requests.post(
                url, headers=headers, data=data, timeout=10)
            response.raise_for_status()
            return response.json().get("access_token")
        except Exception as e:
            logger.error(f"Failed to get PayPal access token: {str(e)}")
            raise

    def post(self, request):
        order_id = request.data.get('order_id')

        if not order_id:
            return Response(
                {"error": "order_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payment_record = Payment.objects.get(paypal_order_id=order_id)
        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            # Get PayPal access token
            access_token = self.get_access_token()

            # Capture PayPal order
            url = f"{settings.PAYPAL_API_BASE_URL}/v2/checkout/orders/{order_id}/capture"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }

            response = requests.post(url, headers=headers, timeout=10)
            capture_data = response.json()

            if response.status_code == 201:
                # Update payment status
                payment_record.status = 'completed'
                payment_record.save()

                # Update item
                item = payment_record.item
                item.highest_bidder = request.user
                item.save()

                return Response({
                    "message": "Payment completed successfully",
                    "order_id": order_id
                }, status=status.HTTP_200_OK)
            else:
                logger.error(f"PayPal capture failed: {capture_data}")
                payment_record.status = 'failed'
                payment_record.save()
                return Response(
                    {"error": capture_data.get(
                        'message', 'Failed to capture payment'), "details": capture_data},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            logger.error(
                f"Error capturing PayPal order: {str(e)}", exc_info=True)
            payment_record.status = 'failed'
            payment_record.save()
            return Response(
                {"error": f"Internal server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payments = Payment.objects.filter(user=request.user)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetPaymentByItemId(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, item_id):
        print('trying to get payment', item_id)
        try:
            item = Item.objects.get(pk=item_id)
        except Item.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND("Item not found")
        print('got item', item)

        payment = Payment.objects.filter(item=item)
        print('got payment', payment)
        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_200_OK)
