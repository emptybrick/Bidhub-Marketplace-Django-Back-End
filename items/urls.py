from django.urls import path
from .views import ItemListView, ItemDetailView, CreateItem, UpdateShippingAndPaymentView

urlpatterns = [
    # Base item endpoints
    path('', ItemListView.as_view()),
    path('new/', CreateItem.as_view()),
    path('<int:item_id>/', ItemDetailView.as_view()),
    path('<int:item_id>/shipping-and-payment',
         UpdateShippingAndPaymentView.as_view()),
]
