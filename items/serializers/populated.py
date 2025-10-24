from .common import ItemSerializer
from authentication.serializers import UsernameSerializer
from bids.serializer import BidSerializer

class PopulatedItemSerializer(ItemSerializer):
    owner = UsernameSerializer(read_only=True)
    final_bidder = UsernameSerializer(read_only=True)
    bid_history = BidSerializer(read_only=True)