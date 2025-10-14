from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound

from .models import Item
from .serializers.common import itemserializer
from .serializers.populated import Populateditemserializer
# IsAuthenticatedOrReadOnly specifies that a view is secure on all methods except get requests
from rest_framework.permissions import IsAuthenticatedOrReadOnly

# Create your views here.


class ItemListView(APIView):
    # sets the permission levels of the specific view by passing in the rest framework authentication class
    permission_classes = (IsAuthenticatedOrReadOnly, )
    # handle a GET request in the ItemListView

    def get(self, _request):
        # go to the database and get all the items
        items = Item.objects.all()
        # translate the items from the database to a usable form
        serialized_items = itemserializer(items, many=True)
        # return the serialized data and a 200 status code
        return Response(serialized_items.data, status=status.HTTP_200_OK)

    def post(self, request):
        request.data["owner"] = request.user.id
        Item_to_add = itemserializer(data=request.data)
        try:
            Item_to_add.is_valid()
            Item_to_add.save()
            return Response(Item_to_add.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print("Error")
            # the below is necessary because two different formats of errors are possible. string or object format.
            # if it's string then e.__dict__ returns an empty dict {}
            # so we'll check it's a dict first, and if it's empty (falsey) then we'll use str() to convert to a string
            return Response(e.__dict__ if e.__dict__ else str(e), status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class ItemDetailView(APIView):
    # sets the permission levels of the specific view by passing in the rest framework authentication class
    permission_classes = (IsAuthenticatedOrReadOnly, )

    # custom method to retrieve a Item from the DB and error if it's not found
    def get_Item(self, pk):
        try:
            return Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            # <-- import the NotFound exception from rest_framwork.exceptions
            raise NotFound(detail="Can't find that Item")

    def get(self, _request, pk):
        try:
            Item = Item.objects.get(pk=pk)
            serialized_Item = Populateditemserializer(Item)
            return Response(serialized_Item.data, status=status.HTTP_200_OK)
        except Item.DoesNotExist:
            # <-- import the NotFound exception from rest_framwork.exceptions
            raise NotFound(detail="Can't find that Item")

    def put(self, request, pk):
        Item_to_update = self.get_Item(pk=pk)
        if Item_to_update.owner != request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        updated_Item = itemserializer(Item_to_update, data=request.data)
        if updated_Item.is_valid():
            updated_Item.save()
            return Response(updated_Item.data, status=status.HTTP_202_ACCEPTED)

        return Response(updated_Item.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def delete(self, request, pk):
        Item_to_delete = self.get_Item(pk=pk)

        if Item_to_delete.owner != request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        Item_to_delete.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
