from .common import itemserializer
from authors.serializers.common import AuthorSerializer
from authentication.serializers import UserSerializer
from comments.serializers.populated import PopulatedCommentSerializer


class Populateditemserializer(itemserializer):
    author = AuthorSerializer()
    owner = UserSerializer()
    comments = PopulatedCommentSerializer(many=True)
