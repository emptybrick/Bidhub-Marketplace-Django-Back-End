from .common import ReviewSerializer
from authentication.serializers import UserSerializer

class PopulatedReviewSerializer(ReviewSerializer):
    """Enriched review serializer with user details"""
    author = UserSerializer(read_only=True)
    seller_id = UserSerializer(read_only=True)

    rating_breakdown = serializers.SerializerMethodField()

    class Meta(ReviewSerializer.Meta):
        fields = ReviewSerializer.Meta.fields + ['rating_breakdown']

    def get_rating_breakdown(self, obj):
        """Provide detailed breakdown of different rating aspects"""
        return {
            'service': {
                'score': obj.service_rating,
                'percentage': obj.service_rating * 10
            },
            'product': {
                'score': obj.product_rating,
                'percentage': obj.product_rating * 10
            },
            'packaging': {
                'score': obj.packaging_rating,
                'percentage': obj.packaging_rating * 10
            },
            'shipping': {
                'score': obj.shipping_rating,
                'percentage': obj.shipping_rating * 10
            },
            'overall': {
                'score': obj.overall_rating,
                'percentage': obj.overall_rating * 10
            }
        }
