from .common import ReviewSerializer
from authentication.serializers import UserSerializer

class PopulatedReviewSerializer(ReviewSerializer):
    """Enriched review serializer with user details"""
    author = UserSerializer(read_only=True)
    seller_id = UserSerializer(read_only=True)

    # class Meta(ReviewSerializer.Meta):
    #     fields = '__all__'
