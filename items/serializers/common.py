from rest_framework import serializers
# from django.utils import timezone
from ..models import Item


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


class ShippingAndPaymentSerializer(serializers.ModelSerializer):
    shipping_info = serializers.JSONField()

    class Meta:
        model = Item
        fields = ['shipping_info', 'payment_confirmation']
