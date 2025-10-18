from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Bid
from items.models import Item
from .serializer import BidSerializer
from items.serializers.common import ItemSerializer
# from .serializers.common import BidSerializer
# from .serializers.populated import PopulatedBidSerializer


class CreateBid(APIView):
    def post(self, request, item_id):
        """Create a new bid for an item"""
        try:
            # Check if item exists
            item = Item.objects.get(pk=item_id)

            if item.owner.id == request.user.id:
                return Response({"detail": "Cannot bid on your own item"}, status=status.HTTP_400_BAD_REQUEST)

            # Check if auction has ended
            if item.end_time and item.end_time < timezone.now():
                return Response({"detail": "Auction has ended"}, status=status.HTTP_400_BAD_REQUEST)

            # Get highest bid for this item and compare to bid offer
            current_bid = item.current_bid
            if current_bid >= request.data["bid"]:
                return Response({"detail": "Bid offer is lower than or equal to current bid"}, status=status.HTTP_400_BAD_REQUEST)

            # Set the bidder to current user and item to the specified item
            bid_data = request.data.copy()
            bid_data['user_id'] = request.user.id
            bid_data['item_id'] = item_id
            item.highest_bidder = request.user
            # Create serializer with the data
            bid_to_create = BidSerializer(data=bid_data)

            if not bid_to_create.is_valid(raise_exception=True):
                return Response(BidSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            bid_to_create.save()

            item_data = {
                'highest_bidder': request.user.id,
                'current_bid': request.data["bid"]  # Update current_bid here
            }

            item_serializer = ItemSerializer(
                instance=item, data=item_data, partial=True)

            if not item_serializer.is_valid(raise_exception=True):
                # Will rollback transaction
                return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            item_serializer.save()

            return Response(bid_to_create.data, status=status.HTTP_201_CREATED)

        except Item.DoesNotExist:
            raise NotFound(detail="Item not found")
        except Exception as e:
            return Response({"exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# class BidListView(APIView):
#     """View for getting all bids for a specific item or creating a new bid"""
#     permission_classes = (IsAuthenticatedOrReadOnly,)

#     def get(self, request, item_id):
#         """Get all bids for a specific item with filtering and sorting options"""
#         try:
#             # Verify the item exists first
#             item = Item.objects.get(pk=item_id)

#             # Initialize queryset
#             bids = Bid.objects.filter(item=item_id)

#             # Date range filtering
#             start_date = request.query_params.get('start_date')
#             end_date = request.query_params.get('end_date')
#             recent = request.query_params.get('recent')

#             if start_date:
#                 try:
#                     start_datetime = datetime.fromisoformat(start_date)
#                     bids = bids.filter(created_at__gte=start_datetime)
#                 except ValueError:
#                     return Response({"detail": "Invalid start_date format. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"},
#                                     status=status.HTTP_400_BAD_REQUEST)

#             if end_date:
#                 try:
#                     end_datetime = datetime.fromisoformat(end_date)
#                     bids = bids.filter(created_at__lte=end_datetime)
#                 except ValueError:
#                     return Response({"detail": "Invalid end_date format. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"},
#                                     status=status.HTTP_400_BAD_REQUEST)

#             # Recent bids filtering
#             if recent:
#                 if recent == '24h':
#                     bids = bids.filter(
#                         created_at__gte=timezone.now() - timedelta(hours=24))
#                 elif recent == '7d':
#                     bids = bids.filter(
#                         created_at__gte=timezone.now() - timedelta(days=7))
#                 elif recent == '30d':
#                     bids = bids.filter(
#                         created_at__gte=timezone.now() - timedelta(days=30))

#             # Sorting
#             sort_field = request.query_params.get('sort', 'amount')
#             sort_direction = request.query_params.get('direction', 'desc')

#             # Validate sort field to prevent injection
#             allowed_fields = ['amount', 'created_at', 'updated_at']
#             if sort_field not in allowed_fields:
#                 sort_field = 'amount'

#             # Apply sorting direction
#             order_by = f"{'-' if sort_direction.lower() == 'desc' else ''}{sort_field}"
#             bids = bids.order_by(order_by)

#             # Pagination
#             paginator = PageNumberPagination()
#             paginator.page_size = 10
#             result_page = paginator.paginate_queryset(bids, request)
#             serialized_bids = PopulatedBidSerializer(result_page, many=True)
#             return paginator.get_paginated_response(serialized_bids.data)

#         except Item.DoesNotExist:
#             raise NotFound(detail="Item not found")

#     def post(self, request, item_id):
#         """Create a new bid for an item"""
#         try:
#             # Check if item exists
#             item = Item.objects.get(pk=item_id)

#             # Check if auction has ended
#             if item.auction_end and item.auction_end < timezone.now():
#                 return Response({"detail": "Auction has ended"}, status=status.HTTP_400_BAD_REQUEST)

#             # Get highest bid for this item
#             highest_bid = Bid.objects.filter(
#                 item=item_id).order_by('-amount').first()

#             # Set the bidder to current user and item to the specified item
#             request.data["bidder"] = request.user.id
#             request.data["item"] = item_id

#             # Create serializer with the data
#             bid_to_create = BidSerializer(data=request.data)

#             if bid_to_create.is_valid():
#                 # Check if bid is higher than current highest bid or starting price
#                 bid_amount = bid_to_create.validated_data["amount"]

#                 if highest_bid and bid_amount <= highest_bid.amount:
#                     return Response(
#                         {"detail": f"Bid must be higher than current highest bid (${highest_bid.amount})"},
#                         status=status.HTTP_400_BAD_REQUEST
#                     )
#                 elif not highest_bid and bid_amount < item.starting_price:
#                     return Response(
#                         {"detail": f"Bid must be at least the starting price (${item.starting_price})"},
#                         status=status.HTTP_400_BAD_REQUEST
#                     )

#                 # Save the bid if it passes validation
#                 bid_to_create.save()
#                 return Response(bid_to_create.data, status=status.HTTP_201_CREATED)

#             return Response(bid_to_create.errors, status=status.HTTP_400_BAD_REQUEST)

#         except Item.DoesNotExist:
#             raise NotFound(detail="Item not found")
#         except Exception as e:
#             return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# class BidDetailView(APIView):
#     """View for retrieving or canceling a specific bid"""
#     permission_classes = (IsAuthenticated,)

#     def get_bid(self, pk):
#         """Helper method to get a bid by primary key"""
#         try:
#             return Bid.objects.get(pk=pk)
#         except Bid.DoesNotExist:
#             raise NotFound(detail="Bid not found")

#     def get(self, request, pk):
#         """Get a specific bid"""
#         bid = self.get_bid(pk)
#         serialized_bid = PopulatedBidSerializer(bid)
#         return Response(serialized_bid.data, status=status.HTTP_200_OK)


# class UserBidsView(APIView):
#     """View for getting all bids by the current user"""
#     permission_classes = (IsAuthenticated,)

#     def get(self, request):
#         """Get all bids made by the current user with filtering and sorting options"""
#         # Initialize queryset
#         bids = Bid.objects.filter(bidder=request.user)

#         # Date range filtering
#         start_date = request.query_params.get('start_date')
#         end_date = request.query_params.get('end_date')
#         recent = request.query_params.get('recent')

#         if start_date:
#             try:
#                 start_datetime = datetime.fromisoformat(start_date)
#                 bids = bids.filter(created_at__gte=start_datetime)
#             except ValueError:
#                 return Response({"detail": "Invalid start_date format. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"},
#                                 status=status.HTTP_400_BAD_REQUEST)

#         if end_date:
#             try:
#                 end_datetime = datetime.fromisoformat(end_date)
#                 bids = bids.filter(created_at__lte=end_datetime)
#             except ValueError:
#                 return Response({"detail": "Invalid end_date format. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"},
#                                 status=status.HTTP_400_BAD_REQUEST)

#         # Recent bids filtering
#         if recent:
#             if recent == '24h':
#                 bids = bids.filter(
#                     created_at__gte=timezone.now() - timedelta(hours=24))
#             elif recent == '7d':
#                 bids = bids.filter(
#                     created_at__gte=timezone.now() - timedelta(days=7))
#             elif recent == '30d':
#                 bids = bids.filter(
#                     created_at__gte=timezone.now() - timedelta(days=30))

#         # Sorting
#         sort_field = request.query_params.get('sort', 'created_at')
#         sort_direction = request.query_params.get('direction', 'desc')

#         # Validate sort field to prevent injection
#         allowed_fields = ['amount', 'created_at', 'updated_at']
#         if sort_field not in allowed_fields:
#             sort_field = 'created_at'

#         # Apply sorting direction
#         order_by = f"{'-' if sort_direction.lower() == 'desc' else ''}{sort_field}"
#         bids = bids.order_by(order_by)

#         # Apply pagination
#         paginator = PageNumberPagination()
#         paginator.page_size = 10
#         result_page = paginator.paginate_queryset(bids, request)
#         serialized_bids = PopulatedBidSerializer(result_page, many=True)
#         return paginator.get_paginated_response(serialized_bids.data)
