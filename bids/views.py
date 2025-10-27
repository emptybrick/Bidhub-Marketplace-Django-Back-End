import decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from django.utils import timezone

from items.models import Item
from .serializer import BidSerializer
from items.serializers.common import ItemBidUpdateSerializer


class CreateBid(APIView):
    def post(self, request, item_id):
        """Create a new bid for an item"""
        bid_str = request.data["bid"]
        try:
            # Check if item exists
            item = Item.objects.get(pk=item_id)
            # assign request data to variable
            bid = decimal.Decimal(bid_str)
            if item.owner.id == request.user.id:
                return Response({"detail": "Cannot bid on your own item"}, status=status.HTTP_400_BAD_REQUEST)
            # Check if auction has ended
            if item.end_time and item.end_time < timezone.now():
                return Response({"detail": "Auction has ended"}, status=status.HTTP_400_BAD_REQUEST)
            # prevent negative bids and bids of 0
            if bid <= 0:
                return Response({"detail": "Bid must be greater than zero"}, status=status.HTTP_400_BAD_REQUEST)

            # Get highest bid for this item and compare to bid offer
            current_bid = item.current_bid
            if current_bid >= bid:

                return Response({"detail": "Bid offer is lower than or equal to current bid"}, status=status.HTTP_400_BAD_REQUEST)

            # Set the bidder to current user and item to the specified item
            bid_data = request.data.copy()
            bid_data['user_id'] = request.user.id
            bid_data['item_id'] = item.id
            item.highest_bidder = request.user
            # Create serializer with the data
            bid_to_create = BidSerializer(data=bid_data)

            if not bid_to_create.is_valid(raise_exception=True):
                return Response(BidSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

            bid_to_create.save()

            hidden_username = request.user.username[0] + \
                "***" + request.user.username[-1]

            bid_history = item.bid_history_json or []

            new_bid = {"bidder": hidden_username, "bid": bid_str }
            
            bid_history.insert(0, new_bid)

            item_data = {
                'highest_bidder': request.user.id,
                'current_bid': request.data["bid"],  # Update current_bid here
                'bid_history_json': bid_history
            }

            item_serializer = ItemBidUpdateSerializer(
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
