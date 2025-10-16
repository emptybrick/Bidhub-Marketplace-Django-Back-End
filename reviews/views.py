# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.exceptions import NotFound
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
# from rest_framework.pagination import PageNumberPagination
# from django.db.models import Avg, Q

# from .models import Review
# from items.models import Item  # Import Item from items app
# from .serializers.common import ReviewsSerializer
# from .serializers.populated import PopulatedReviewSerializer
# from django.utils import timezone


# class ReviewPagination(PageNumberPagination):
#     page_size = 10
#     page_size_query_param = 'page_size'
#     max_page_size = 50


# class ReviewListView(APIView):
#     permission_classes = (IsAuthenticated,)
#     pagination_class = ReviewPagination

#     def post(self, request):
#         """Create a new review for a seller"""
#         # Set author to the current user
#         request.data["author"] = request.user.id

#         seller_id = request.data.get("seller_id")

#         if not Item.objects.filter(
#             owner=seller_id,
#             # end_time from items model when auction ends, __lt "less than", timezone.now().
#             end_time__lt=timezone.now(),
#             final_bidder=request.user,  # User is the winning bidder
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


# class SellerReviewsView(APIView):
#     """View for getting all reviews for a specific seller"""
#     permission_classes = (IsAuthenticatedOrReadOnly,)
#     pagination_class = ReviewPagination

#     def get(self, request, seller_id):
#         """Get all reviews for a seller with filtering and sorting"""
#         reviews = Review.objects.filter(seller_id=seller_id)

#         # Sort options refer to sellerpage.jsx for sort options in frontend
#         sort_by = request.query_params.get(
#             'sort', '-created_at')  # Default newest first
#         if sort_by not in ['created_at', '-created_at', 'rating', '-rating']:
#             sort_by = '-created_at'  # Default to newest

#         # Takes the queryset of reviews and orders them by the chosen field
#         reviews = reviews.order_by(sort_by)

#         # Get average ratings for the seller. Calculates average ratings across 5 categories.
#         avg_ratings = Review.objects.filter(seller_id=seller_id).aggregate(  # aggregate - calculate at database level.
#             avg_overall=Avg('overall_rating'),
#             avg_service=Avg('service_rating'),
#             avg_product=Avg('product_rating'),
#             avg_packaging=Avg('packaging_rating'),
#             avg_shipping=Avg('shipping_rating')
#         )

#         # Paginate results
#         paginator = self.pagination_class()
#         page = paginator.paginate_queryset(reviews, request)

#         serializer = PopulatedReviewSerializer(page, many=True)
#         response = paginator.get_paginated_response(serializer.data)

#         # Seller average ratings to response
#         response.data['seller_ratings'] = avg_ratings

#         return response


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
