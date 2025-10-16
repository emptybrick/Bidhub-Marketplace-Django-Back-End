from django.urls import path
from .views import ReviewListView, ReviewDetailView, SellerReviewsView, UserReviewsView

urlpatterns = [
    # Create new review
    path('', ReviewListView.as_view()),

    # Get reviews for a specific seller with sorting options
    # /api/reviews/sellers/5/?sort=-rating
    path('sellers/<int:seller_id>/', SellerReviewsView.as_view()),

    # Get/update/delete a specific review
    path('<int:pk>/', ReviewDetailView.as_view()),

    # Current user's written reviews
    path('my-reviews/', UserReviewsView.as_view()),

    # Filter reviews by rating range
    # /api/reviews/sellers/5/rating/4-5/
    path('sellers/<int:seller_id>/rating/<str:rating_range>/',
         SellerReviewsView.as_view()),

    # Get top-rated sellers
   # path('top-sellers/', TopSellerReviewsView.as_view()),

    # Get most recent reviews across platform
   # path('recent/', RecentReviewsView.as_view()),
]
