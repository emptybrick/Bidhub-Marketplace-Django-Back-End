from django.urls import path
from .views import ItemListView, ItemDetailView

urlpatterns = [
    path('marketplace/', ItemListView.as_view()),
    path('marketplace/<int:pk>/', ItemDetailView.as_view()),
]
