from .common import ItemSerializer
from authentication.serializers import UserSerializer
from reviews.serializers.populated import PopulatedReviewSerializer 


class PopulatedItemSerializer(ItemSerializer):
    author = UserSerializer()
    owner = UserSerializer()
    reviews = PopulatedReviewSerializer(many=True)  
