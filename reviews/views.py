from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from django.db.models import Avg, Q
from django.forms.models import model_to_dict

from .models import Review
from authentication.models import User
from items.models import Item  # Import Item from items app
from .serializers.common import ReviewSerializer
from .serializers.populated import PopulatedReviewSerializer
from authentication.serializers import UserSerializer
from django.utils import timezone


def GetAverageRating(review_data):
    # recieving review data from the initial request to get an average and return
    average_rating = (review_data['service_rating'] + review_data['product_rating'] + review_data[
        'packaging_rating'] + review_data['shipping_rating'] + review_data['overall_rating'])/10

    return average_rating


def UpdateSellerRating(seller_id, review_data, seller):
    review_data["rating"] = GetAverageRating(review_data)

    # average review ratings to update seller rating
    seller_average_rating = Review.objects.filter(
        seller_id=seller_id).aggregate(Avg('rating'))['rating__avg']

    # Check if this is the first review (no previous average)
    if seller_average_rating is None:
        # If this is the first review, use the current review rating
        seller_average_rating = review_data["rating"]
    else:
        # Round to 2 decimal places
        seller_average_rating = round(seller_average_rating, 2)
    # update seller average rating
    seller_data = {
        'user_rating': seller_average_rating
    }
    # sets partial data to serializer
    seller_serializer = UserSerializer(
        instance=seller, data=seller_data, partial=True)

    # checks if seller data is valid before save
    if seller_serializer.is_valid():
        seller_serializer.save()
        return Response(seller_serializer.data, status=status.HTTP_200_OK)

    return Response(seller_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class CreateReview(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, seller_id):
        """Create a new review for a seller"""

        # get item and seller data
        try:
            seller = User.objects.get(pk=seller_id)
        except (User.DoesNotExist):
            return Response(
                {"detail": "Seller not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # check if user has permission to leave review by comparing author,
        # highest_bidder, and making sure auction has ended
        if not Item.objects.filter(
            owner=seller,
            highest_bidder=request.user,
            end_time__lt=timezone.now()
        ).exists():
            return Response(
                {"detail": "You can only review sellers you've purchased from after the auction has ended"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if user has already reviewed the seller
        reviews_by_user = Review.objects.filter(
            author=request.user)
        if reviews_by_user.exists():
            return Response(
                {"detail": "You have already reviewed this seller."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Set author, seller and item info
        review_data = request.data.copy()
        review_data["author"] = request.user.id
        review_data["seller_id"] = seller_id

        # average out review ratings for review.rating
        average_rating = GetAverageRating(review_data)

        review_data["rating"] = average_rating

        review_to_add = ReviewSerializer(data=review_data)

       # checks if review data is valid before save
        if review_to_add.is_valid():
            review_to_add.save()
            UpdateSellerRating(seller_id, review_data, seller)
            return Response(review_to_add.data, status=status.HTTP_200_OK)

        return Response(review_to_add.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewDetails(APIView):
    permission_classes = (IsAuthenticated,)

    def get_review(self, review_id):
        try:
            return Review.objects.get(pk=review_id)
        except Review.DoesNotExist:
            raise NotFound(detail="Review not found")

    def put(self, request, seller_id, review_id):
        review_to_update = self.get_review(review_id)
        seller = User.objects.get(pk=seller_id)

        # Only allow author to update their own review
        if review_to_update.author.id != request.user.id:
            return Response({"detail": "Not authorized to update this review"},
                            status=status.HTTP_403_FORBIDDEN)

        # make copy of request to edit and average out review ratings for review.rating
        review_data = request.data.copy()

        average_rating = GetAverageRating(review_data)

        review_data["rating"] = average_rating

        updated_review = ReviewSerializer(
            review_to_update, data=review_data, partial=True)

        if updated_review.is_valid():
            updated_review.save()
            UpdateSellerRating(seller_id, review_data, seller)
            return Response(updated_review.data, status=status.HTTP_200_OK)

        return Response(updated_review.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, seller_id, review_id):
        review_to_delete = self.get_review(review_id)
        review_data = model_to_dict(review_to_delete)
        seller = review_to_delete.seller_id
        # Only author to delete their own review
        if review_to_delete.author.id != request.user.id:
            return Response({"detail": "Not authorized to delete this review"},
                            status=status.HTTP_403_FORBIDDEN)

        review_to_delete.delete()
        UpdateSellerRating(seller_id, review_data, seller)
        return Response({"detail": "Review has been successfully deleted."}, status=status.HTTP_204_NO_CONTENT)


class SellerReviews(APIView):
    """View for getting all reviews for a specific seller"""
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = ReviewPagination

    def get(self, request, seller_id):
        """Get all reviews for a seller with filtering and sorting"""
        reviews = Review.objects.filter(seller_id=seller_id)

        # Sort options refer to sellerpage.jsx for sort options in frontend
        sort_by = request.query_params.get(
            'sort', '-created_at')  # Default newest first
        if sort_by not in ['created_at', '-created_at', 'rating', '-rating']:
            sort_by = '-created_at'  # Default to newest

        # Takes the queryset of reviews and orders them by the chosen field
        reviews = reviews.order_by(sort_by)

        # Get average ratings for the seller. Calculates average ratings across 5 categories.
        # avg_ratings = Review.objects.filter(seller_id=seller_id).aggregate(  # aggregate - calculate at database level.
        #     avg_overall=Avg('overall_rating'),
        #     avg_service=Avg('service_rating'),
        #     avg_product=Avg('product_rating'),
        #     avg_packaging=Avg('packaging_rating'),
        #     avg_shipping=Avg('shipping_rating')
        # )

        # Paginate results
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(reviews, request)

        serializer = PopulatedReviewSerializer(page, many=True)
        response = paginator.get_paginated_response(serializer.data)

        return response


# class ReviewDetailView(APIView):
#     permission_classes = (IsAuthenticated,)

#     # def get_review(self, pk):
#     #     try:
#     #         return Review.objects.get(pk=pk)
#     #     except Review.DoesNotExist:
#     #         raise NotFound(detail="Review not found")

#     def post(self, request, pk):
#         """Create a new review for a seller"""
#         # Set author to the current user
#         request.data["author"] = request.user.id

#         # Check if user has purchased from this seller
#         seller_id = request.data.get("seller_id")

#         if not Item.objects.filter(
#             owner=seller_id,
#             # end_time from items model when auction ends, __lt "less than", timezone.now().
#             end_time__lt=timezone.now(),
#             final_bidder=request.user,  # User is the winning bidder * Review technique to determine final bidder. final_bidder = placeholder.
#         ).exists():
#             return Response(
#                 {"detail": "You can only review sellers you've purchased from"},
#                 status=status.HTTP_403_FORBIDDEN
#             )

#         # Disable user from setting these fields
#         if "created_at" in request.data:
#             # wouldnt this be handled by not having option in form field? Ok let me check this out.
#             del request.data["created_at"]

#         review_to_add = ReviewsSerializer(data=request.data)

#         if review_to_add.is_valid():
#             review_to_add.save()
#             return Response(review_to_add.data, status=status.HTTP_201_CREATED)

#         return Response(review_to_add.errors, status=status.HTTP_400_BAD_REQUEST)

#     def get(self, request, pk):  # request not accessed/used
#         review = self.get_review(pk=pk)
#         serialized_review = PopulatedReviewSerializer(review)
#         return Response(serialized_review.data, status=status.HTTP_200_OK)

#     def put(self, request, pk):
#         review_to_update = self.get_review(pk=pk)

#         # Only allow author to update their own review
#         if review_to_update.author.id != request.user.id:
#             return Response({"detail": "Not authorized to update this review"},
#                             status=status.HTTP_403_FORBIDDEN)

#         # Don't allow changing the seller or author
#         if "seller_id" in request.data:
#             del request.data["seller_id"]
#         if "author" in request.data:
#             del request.data["author"]
#         if "created_at" in request.data:
#             del request.data["created_at"]

#         updated_review = ReviewsSerializer(
#             review_to_update, data=request.data, partial=True)

#         if updated_review.is_valid():
#             updated_review.save()
#             return Response(updated_review.data, status=status.HTTP_200_OK)

#         return Response(updated_review.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         review_to_delete = self.get_review(pk=pk)

#         # Only author to delete their own review
#         if review_to_delete.author.id != request.user.id:
#             return Response({"detail": "Not authorized to delete this review"},
#                             status=status.HTTP_403_FORBIDDEN)

#         review_to_delete.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class UserReviewsView(APIView):
#     """View for getting all reviews written by the current user"""
#     permission_classes = (IsAuthenticated,)
#     pagination_class = ReviewPagination

#     def get(self, request):
#         reviews = Review.objects.filter(
#             author=request.user).order_by('-created_at')

#         paginator = self.pagination_class()
#         page = paginator.paginate_queryset(reviews, request)

#         serializer = PopulatedReviewSerializer(page, many=True)
#         return paginator.get_paginated_response(serializer.data)

# class ReviewPagination(PageNumberPagination):
#     page_size = 10
#     page_size_query_param = 'page_size'
#     max_page_size = 50
