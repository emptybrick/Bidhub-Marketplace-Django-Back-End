from .common import itemserializer
from authentication.serializers import UserSerializer
from reviews.serializers.populated import PopulatedReviewsSerializer

class Populateditemserializer(itemserializer):
    author = UserSerializer()
    owner = UserSerializer()
    reviews = PopulatedReviewsSerializer(many=True)
