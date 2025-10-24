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
from decimal import Decimal

class ReviewPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


def GetAverageRating(review_data):
    # Sum the 5 rating components and divide by 5
    ratings = [
        review_data.get('service_rating', 0),
        review_data.get('product_rating', 0),
        review_data.get('packaging_rating', 0),
        review_data.get('shipping_rating', 0),
        review_data.get('overall_rating', 0)
    ]
    # Ensure ratings are numeric and handle missing/invalid data
    valid_ratings = [float(r) for r in ratings if r is not None]
    return round(sum(valid_ratings) / 10, 2) if valid_ratings else 0.01


def UpdateSellerRating(seller_id, review_data, seller):
    # Calculate average rating from all reviews for the seller
    seller_average_rating = Review.objects.filter(
        seller_id=seller_id).aggregate(Avg('rating'))['rating__avg']

    # Handle case where no reviews exist
    if seller_average_rating is None:
        seller_average_rating = Decimal('0.01')
    else:
        seller_average_rating = Decimal(f'{seller_average_rating:.2f}')

    # Ensure minimum value
    if seller_average_rating < Decimal('0.01'):
        seller_average_rating = Decimal('0.01')

    # Prepare data for serializer
    seller_data = {'user_rating': seller_average_rating}
    print(f"Updating seller {seller_id} with user_rating: {seller_data}")

    # Update seller using serializer
    seller_serializer = UserSerializer(
        instance=seller, data=seller_data, partial=True)

    if seller_serializer.is_valid():
        seller_serializer.save()
        print(
            f"Successfully updated seller {seller_id} with user_rating: {seller_average_rating}")
        return Response(seller_serializer.data, status=status.HTTP_200_OK)

    print(f"Serializer errors: {seller_serializer.errors}")
    return Response(seller_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            owner_id=seller.id,
            highest_bidder_id=request.user.id,
            end_time__lt=timezone.now()
        ).exists():
            return Response(
                {"detail": "You can only review sellers you've purchased from after the auction has ended"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if user has already reviewed the seller
        reviews_by_user = Review.objects.filter(
            author_id=request.user.id
            )
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
        print(request.query_params)
        """Get all reviews for a seller with filtering and sorting"""
        reviews = Review.objects.filter(seller_id=seller_id)

        # Sort options refer to sellerpage.jsx for sort options in frontend
        sort_by_date = request.query_params.get('dateSort', 'none')
        sort_by_rating = request.query_params.get('ratingSort', 'none')
        print("getting reviews, and sorting by: ", sort_by_date, sort_by_rating)
        if sort_by_date != 'none':
            if sort_by_date == 'asc':
                reviews = reviews.order_by("created_at")
            elif sort_by_date == 'desc':
                reviews = reviews.order_by("-created_at")
        if sort_by_rating != 'none':
            if sort_by_rating == 'asc':
                reviews = reviews.order_by("rating")
            elif sort_by_rating == 'desc':
                reviews = reviews.order_by("-rating")

        # Paginate results
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(reviews, request)

        serializer = PopulatedReviewSerializer(page, many=True)
        response = paginator.get_paginated_response(serializer.data)

        return response
