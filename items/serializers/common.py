from rest_framework import serializers
from ..models import Item


class itemserializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'
