from django.urls import path
from payments.views import CreateOrderView, CaptureOrderView, GetPaymentByItemId

urlpatterns = [
    path('create-order/', CreateOrderView.as_view(), name='create_order'),
    path('capture-order/', CaptureOrderView.as_view(), name='capture_order'),
    path('get-payment/<int:item_id/', GetPaymentByItemId.as_view())
]
