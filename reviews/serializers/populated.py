from .common import ReviewsSerializer
from authentication.serializers import UserSerializer


class PopulatedReviewsSerializer(ReviewsSerializer):
    owner = UserSerializer()
    # Add other fields as needed
