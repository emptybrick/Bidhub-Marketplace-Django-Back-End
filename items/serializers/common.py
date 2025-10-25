from rest_framework import serializers
# from django.utils import timezone
from ..models import Item
from django.utils import timezone


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

    def validate_end_time(self, value):
        """Ensure end_time is not in the past."""
        if value < timezone.now():
            raise serializers.ValidationError(
                "End time cannot be earlier than the current time.")
        return value

class ItemBidUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields =[ 'bid_history_json', 'highest_bidder', 'current_bid']

class ShippingAndPaymentSerializer(serializers.ModelSerializer):
    shipping_info = serializers.JSONField()

    class Meta:
        model = Item
        fields = ['shipping_info', 'payment_confirmation']
