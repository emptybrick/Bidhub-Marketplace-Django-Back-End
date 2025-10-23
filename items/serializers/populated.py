from .common import ItemSerializer
from authentication.serializers import UsernameSerializer
from reviews.serializers.populated import PopulatedReviewSerializer
from bids.serializer import BidSerializer
# from django.utils import timezone

class PopulatedItemSerializer(ItemSerializer):
    owner = UsernameSerializer(read_only=True)
    final_bidder = UsernameSerializer(read_only=True)
    reviews = PopulatedReviewSerializer(many=True, read_only=True)
    bid_history = BidSerializer(read_only=True)

 