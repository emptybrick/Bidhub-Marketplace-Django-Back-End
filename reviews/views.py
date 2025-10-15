from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework import status

from .models import Review
from .serializers.common import ReviewsSerializer
from rest_framework.permissions import IsAuthenticated


class ReviewListView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        print("CREATING COMMMENT USER ID", request.user.id)
        request.data["owner"] = request.user.id
        review_to_add = ReviewsSerializer(
            data=request.data)
        try:
            review_to_add.is_valid()
            review_to_add.save()
            return Response(review_to_add.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print("Error")
            return Response(e.__dict__ if e.__dict__ else str(e), status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class ReviewDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_review(self, pk):
        try:
            return Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            raise NotFound(detail="Can't find that Review")

    def get(self, request, pk):
        review = self.get_review(pk=pk)
        serialized_review = ReviewsSerializer(review)
        return Response(serialized_review.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        review_to_update = self.get_review(pk=pk)

        if review_to_update.owner != request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        updated_review = ReviewsSerializer(review_to_update, data=request.data)

        if updated_review.is_valid():
            updated_review.save()
            return Response(updated_review.data, status=status.HTTP_202_ACCEPTED)

        return Response(updated_review.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def delete(self, request, pk):
        review_to_delete = self.get_review(pk=pk)

        if review_to_delete.owner != request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        review_to_delete.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
