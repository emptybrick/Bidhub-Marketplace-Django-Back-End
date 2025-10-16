from .common import ReviewsSerializer
from authentication.serializers import UserSerializer


class PopulatedReviewSerializer(ReviewsSerializer):  # Removed the 's'
    owner = UserSerializer()
    # Add other fields as needed
