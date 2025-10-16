from django.urls import path
from .views import ItemListView, ItemDetailView

urlpatterns = [
    # Base item endpoints
    path('', ItemListView.as_view()),
    path('<int:pk>/', ItemDetailView.as_view()),

    # # Category endpoints
    # path('categories/<str:category>/', ItemListView.as_view()),

    # # User-specific endpoints
    # path('sellers/<int:seller_id>/', ItemListView.as_view()),
    # path('my-listings/', ItemListView.as_view()),
    # path('my-watching/', ItemListView.as_view()),

    # # Time-based endpoints
    # path('ending-soon/', ItemListView.as_view()),
    # path('newly-listed/', ItemListView.as_view()),

    # # Auction status endpoints
    # path('active/', ItemListView.as_view()),
    # path('completed/', ItemListView.as_view()),
    # path('no-bids/', ItemListView.as_view()),

    # Related item recommendations
#    path('<int:pk>/related/', ItemListView.as_view()),
#    path('<int:pk>/similar/', ItemListView.as_view()),
]
