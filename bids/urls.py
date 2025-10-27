from django.urls import path
from .views import CreateBid

urlpatterns = [
    path('new/', CreateBid.as_view()),
]