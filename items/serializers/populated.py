from .common import ItemSerializer
from authentication.serializers import UsernameSerializer

class PopulatedItemSerializer(ItemSerializer):
    owner = UsernameSerializer(read_only=True)
    final_bidder = UsernameSerializer(read_only=True)