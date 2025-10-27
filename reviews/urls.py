from django.urls import path
from .views import CreateReview, SellerReviews, ReviewDetails

urlpatterns = [
    path('', SellerReviews.as_view()),
    path('new/', CreateReview.as_view()),
    path('<int:review_id>/', ReviewDetails.as_view()),
]
