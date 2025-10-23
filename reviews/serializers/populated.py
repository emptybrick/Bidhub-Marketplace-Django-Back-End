from .common import ReviewSerializer
from authentication.serializers import UsernameSerializer

class PopulatedReviewSerializer(ReviewSerializer):
    """Enriched review serializer with user details"""
    author = UsernameSerializer(read_only=True)
    seller_id = UsernameSerializer(read_only=True)