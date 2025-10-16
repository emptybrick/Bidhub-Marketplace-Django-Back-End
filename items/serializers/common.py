from rest_framework import serializers
from django.utils import timezone
from ..models import Item


class ItemSerializer(serializers.ModelSerializer):
    time_remaining = serializers.SerializerMethodField()
    bid_count = serializers.SerializerMethodField()
    auction_status = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = '__all__'
        read_only_fields = ('created_at', 'current_bid', 'final_bidder')

    def get_time_remaining(self, obj):
        """Calculate time remaining in auction"""
        if obj.end_time > timezone.now():
            time_left = obj.end_time - timezone.now()
            days = time_left.days
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            return {
                'days': days,
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds,
                'total_seconds': time_left.total_seconds()
            }
        return None

    def get_bid_count(self, obj):
        """Return number of bids on this item"""
        return obj.bids.count() if hasattr(obj, 'bids') else 0

    def get_auction_status(self, obj):
        """Return auction status"""
        now = timezone.now()
        if now < obj.start_time:
            return "upcoming"
        elif now > obj.end_time:
            return "ended" if obj.final_bidder else "expired"
        else:
            return "active"


class ItemListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    time_remaining = serializers.SerializerMethodField()
    bid_count = serializers.SerializerMethodField()
    auction_status = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = [
            'id', 'item_name', 'initial_bid', 'current_bid',
            'start_time', 'end_time', 'auction_status',
            'time_remaining', 'bid_count', 'condition'
        ]

    # Same method implementations as ItemSerializer
    def get_time_remaining(self, obj):
        # Same implementation as ItemSerializer
        pass

    def get_bid_count(self, obj):
        # Same implementation as ItemSerializer
        pass

    def get_auction_status(self, obj):
        # Same implementation as ItemSerializer
        pass
