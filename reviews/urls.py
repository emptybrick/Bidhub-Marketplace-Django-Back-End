from django.urls import path
from .views import ReviewListView, ReviewDetailView, SellerReviewsView, UserReviewsView

urlpatterns = [
    path('list/', ReviewListView.as_view()),
    path('users/<int:seller_id>/<int:pk>/', ReviewDetailView.as_view()),
    path('users/<int:seller_id>/', SellerReviewsView.as_view()),
    # path('user/', UserReviewsView.as_view()), # is this needed?
]

# seller view page will be a layout that every user has, seller_id = user_id, named differently to differentiate between reviews and items and user auth
