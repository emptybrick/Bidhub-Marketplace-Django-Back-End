from .common import CommentSerializer
from authentication.serializers import UserSerializer

class PopulatedCommentSerializer(CommentSerializer):
    owner = UserSerializer()
