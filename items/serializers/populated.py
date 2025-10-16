from .common import ItemSerializer
from authentication.serializers import UserSerializer
from reviews.serializers.populated import PopulatedReviewSerializer
from bids.serializers.common import BidSerializer
from django.utils import timezone

class PopulatedItemSerializer(ItemSerializer):
    owner = UserSerializer(read_only=True)
    final_bidder = UserSerializer(read_only=True)
    reviews = PopulatedReviewSerializer(many=True, read_only=True)
    bid_history = BidSerializer(read_only=True)
    is_watched = serializers.SerializerMethodField()
    similar_items = serializers.SerializerMethodField()

    class Meta(ItemSerializer.Meta):
        fields = ItemSerializer.Meta.fields + ['is_watched', 'similar_items']

    def get_is_watched(self, obj):
        """Check if current user is watching this item"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # This assumes you have a watchlist model or M2M field
            # return request.user.watchlist.filter(id=obj.id).exists()
            return False  # Replace with actual implementation
        return False

    def get_similar_items(self, obj):
        """Get 3 similar items in same category"""
        similar = Item.objects.filter(
            category=obj.category
        ).exclude(
            id=obj.id
        ).filter(
            end_time__gt=timezone.now()
        ).order_by('?')[:3]  # Random selection limited to 3

        return ItemSerializer(similar, many=True).data
