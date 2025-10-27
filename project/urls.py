from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  
    path('bidhub/auth/', include('authentication.urls')),
    path('bidhub/marketplace/', include([
        path('', include('items.urls')),
        path('<int:item_id>/bids/', include('bids.urls')),
    ])),
    path('bidhub/seller/<int:seller_id>/reviews/', include('reviews.urls')),
    path('bidhub/paypal/', include('payments.urls')),
    path('bidhub/payments/', include('payments.urls')),
]
