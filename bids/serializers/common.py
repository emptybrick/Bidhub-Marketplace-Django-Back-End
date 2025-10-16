from rest_framework import serializers
from ..models import Bid

class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = '__all__'
    #     read_only_fields = ('created_at',)
        
    # def validate(self, data):
    #     """
    #     Validate that the bid amount is higher than current highest bid
    #     """
    #     # This would need to get the item and check if this bid is higher
    #     # than the current highest bid for the item
    #     if 'item_id' in data and 'bid' in data:
    #         item = data['item_id']
    #         highest_bid = Bid.objects.filter(item_id=item).order_by('-bid').first()
            
    #         if highest_bid and data['bid'] <= highest_bid.bid:
    #             raise serializers.ValidationError(
    #                 f"Bid must be higher than current highest bid: ${highest_bid.bid}"
    #             )
        
    #     return data