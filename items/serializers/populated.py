from .common import ItemSerializer
from authentication.serializers import UserSerializer
from reviews.serializers.populated import PopulatedReviewSerializer
from bids.serializer import BidSerializer
# from django.utils import timezone

class PopulatedItemSerializer(ItemSerializer):
    owner = UserSerializer(read_only=True)
    final_bidder = UserSerializer(read_only=True)
    reviews = PopulatedReviewSerializer(many=True, read_only=True)
    bid_history = BidSerializer(read_only=True)

 