from rest_framework import serializers
from .common import BidSerializer
from authentication.serializers import UserSerializer
from items.serializers.common import ItemSerializer
from ..models import Bid


class PopulatedBidSerializer(BidSerializer):
    """
    Enriched bid serializer that includes user and item details
    """
    user_id = UserSerializer(read_only=True)
    item_id = ItemSerializer(read_only=True)

    is_highest = serializers.SerializerMethodField()
    outbid = serializers.SerializerMethodField()

    class Meta(BidSerializer.Meta):
        fields = '__all__'  # Keep all original fields

    def get_is_highest(self, obj):
        """
        Check if this bid is currently the highest bid on the item
        """
        highest_bid = Bid.objects.filter(
            item_id=obj.item_id).order_by('-bid').first()
        return highest_bid and highest_bid.id == obj.id

    def get_outbid(self, obj):
        """
        Check if this bid has been outbid by a higher bid
        """
        higher_bids = Bid.objects.filter(
            item_id=obj.item_id,
            bid__gt=obj.bid,
            created_at__gt=obj.created_at
        ).exists()
        return higher_bids
