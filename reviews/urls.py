from django.urls import path
from .views import ReviewListView, ReviewDetailView, SellerReviewsView, UserReviewsView

urlpatterns = [
    path('', ReviewListView.as_view()),
    path('<int:pk>/', ReviewDetailView.as_view()),
    path('seller/<int:seller_id>/', SellerReviewsView.as_view()),
    path('user/', UserReviewsView.as_view()),
]
