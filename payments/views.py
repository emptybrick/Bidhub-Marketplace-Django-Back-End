from django.shortcuts import render

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from decouple import config

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
    access_token = get_access_token(request).content.decode()["access_token"]  # Fetch token
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
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}
    response = requests.post(url, headers=headers)
    data = response.json()
    if response.status_code == 201:
        # Save to DB: e.g., mark order as paid
        return JsonResponse({"status": "success", "details": data})
    return JsonResponse({"error": data}, status=400)