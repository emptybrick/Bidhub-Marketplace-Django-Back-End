from django.urls import path
from payments.views import CreateOrderView, CaptureOrderView, PaymentHistoryView

urlpatterns = [
    path('create-order/', CreateOrderView.as_view(), name='create_order'),
    path('capture-order/', CaptureOrderView.as_view(), name='capture_order'),
    path('history/', PaymentHistoryView.as_view(), name='payment_history'),
]
