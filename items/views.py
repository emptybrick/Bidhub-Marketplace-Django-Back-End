from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone

from .models import Item
from bids.models import Bid
from .serializers.common import ItemSerializer, ShippingAndPaymentSerializer
from .serializers.populated import PopulatedItemSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from bids.serializer import BidSerializer


class ItemPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ItemListView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = ItemPagination
    allowed_page_sizes = [10, 20, 40, 50, 100]  # allowed choices for page_size

    # GET All Items
    def get(self, request):
        """Get filtered list of items with comprehensive search options"""
        category = request.query_params.get(
            'category', 'all')  # Default to 'all'
        condition = request.query_params.get('condition', 'none')
        # logic to filter by seller/user when needed
        owner = request.query_params.get('owner', 'none')
        sort_by_sold = request.query_params.get("sold", 'false')
        sort_by_end = request.query_params.get("end", 'none')
        sort_by_bid = request.query_params.get("bid", 'none')
        sort_by_start = request.query_params.get("start", 'none')
        sort_by_user_bids = request.query_params.get("userbids", 'false')
        sort_by_user_favorites = request.query_params.get("favorites", 'false')
        sort_by_purchased = request.query_params.get('purchased', 'false')
        user = request.user

        if request.user.is_anonymous != True:
            favorites = user.favorites or []

        if sort_by_user_bids != 'false':
            user_bids = Bid.objects.filter(user_id=user).select_related(
                'item_id').prefetch_related('item_id__bids')
            bidded_items = user_bids.values_list(
                'item_id', flat=True).distinct()
            items = Item.objects.filter(
                id__in=bidded_items).select_related('owner')
        elif sort_by_user_favorites != 'false':
            items = Item.objects.filter(id__in=favorites)
        elif sort_by_purchased != 'false':
            items = Item.objects.filter(
                highest_bidder=user,
                end_time__lt=timezone.now()
            )

        else:
            items = Item.objects.all()  # Return all items

        # filter out all items that auction has ended if not sort_by_sold
        if sort_by_sold != "false":
            items = Item.objects.filter(
                owner=user,
                highest_bidder__isnull=False,
                end_time__lt=timezone.now()
            )
        elif sort_by_purchased == 'false':
            items = items.filter(end_time__gt=timezone.now())

        if category != 'all':
            items = items.filter(category=category)
        if condition != "all":
            items = items.filter(condition=condition)
        if owner != "none":
            owner = int(owner)
            items = items.filter(owner_id=owner)

        if sort_by_end != 'none':
            if sort_by_end == 'asc':
                items = items.order_by("end_time")
            elif sort_by_end == 'desc':
                items = items.order_by("-end_time")
        if sort_by_bid != 'none':
            if sort_by_bid == 'asc':
                items = items.order_by("current_bid")
            elif sort_by_bid == 'desc':
                items = items.order_by("-current_bid")
        if sort_by_start != 'none':
            if sort_by_start == 'asc':
                items = items.order_by("start_time")
            elif sort_by_start == 'desc':
                items = items.order_by("-start_time")

        # sanitize page_size param and apply allowed sizes
        page_size_param = request.query_params.get('page_size')
        if page_size_param:
            try:
                page_size_val = int(page_size_param)
            except ValueError:
                page_size_val = None
            if page_size_val not in self.allowed_page_sizes:
                page_size_val = None
        else:
            page_size_val = None

        paginator = self.pagination_class()
        if page_size_val:
            paginator.page_size = page_size_val

        page = paginator.paginate_queryset(items, request, view=self)
        serializer = ItemSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class CreateItem(APIView):
    def post(self, request):
        """Create a new item"""
        request.data["owner"] = request.user.id
        request.data["current_bid"] = request.data["initial_bid"]
        item_to_add = ItemSerializer(data=request.data)

        try:
            item_to_add.is_valid(raise_exception=True)
            item_to_add.save()
            return Response(item_to_add.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(e.__dict__ if hasattr(e, '__dict__') else str(e),
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class ItemDetailView(APIView):
    # only authenticated users can view item details
    permission_classes = (IsAuthenticated,)

    # GET item
    def get_item(self, pk):
        """Helper method to get an item by ID"""
        try:
            return Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            raise NotFound(detail="Item not found")

    def get(self, request, item_id):
        """Get a specific item with auction status and bid information"""
        item = self.get_item(pk=item_id)  # Use helper method
        serialized_item = PopulatedItemSerializer(item)
        data = serialized_item.data
        bid_history = item.bids.all().order_by('-bid')
        bid_serializer = BidSerializer(bid_history, many=True)
        data['bid_history_json'] = bid_serializer.data

        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, item_id):
        """Update an item"""
        item_to_update = self.get_item(pk=item_id)

        if item_to_update.owner.id != request.user.id:
            return Response({"detail": "You Are NOT THE OWNER OF THIS ITEM"}, status=status.HTTP_401_UNAUTHORIZED)

        # Checking if there are bids before allowing edit
        if item_to_update.highest_bidder:
            return Response(
                {"detail": "Unable to edit an auction in progress."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serialized_item = ItemSerializer(
            item_to_update, data=request.data, partial=True)

        try:
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()
            return Response(serialized_item.data, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response(
                e.__dict__ if hasattr(e, '__dict__') else str(e),
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

    def delete(self, request, item_id):
        """Delete an item"""
        item_to_delete = self.get_item(pk=item_id)

        if item_to_delete.owner.id != request.user.id:
            return Response({"detail": "You Are NOT THE OWNER OF THIS ITEM"}, status=status.HTTP_401_UNAUTHORIZED)

        # Checking if there are bids before allowing deletion
        if item_to_delete.highest_bidder:
            return Response(
                {"detail": "Unable to delete an auction in progress."},
                status=status.HTTP_400_BAD_REQUEST
            )

        item_to_delete.delete()
        return Response({"detail": "Item has been successfully deleted."}, status=status.HTTP_204_NO_CONTENT)

class UpdateShippingAndPaymentView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_item(self, pk):
        """Helper method to get an item by ID"""
        try:
            return Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            raise NotFound(detail="Item not found")

    def put(self, request, item_id):
        """Update an item"""
        item_to_update = self.get_item(pk=item_id)

        # check if auction has ended
        if item_to_update.end_time >= timezone.now():
            return Response({"detail": "Item auction is still in progress."}, status=status.HTTP_412_PRECONDITION_FAILED)

        # check if user is highest bidder (winner)
        if item_to_update.highest_bidder is not None and item_to_update.highest_bidder != request.user:
            return Response({"detail": "You are not authorized to update this item."}, status=status.HTTP_401_UNAUTHORIZED)

        shipping_info = request.data.get('shipping_info', {})
        payment_confirmation = request.data.get('payment_confirmation')

        serializer = ShippingAndPaymentSerializer(
            item_to_update, data={'shipping_info': shipping_info, 'payment_confirmation': payment_confirmation}, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Shipping information updated successfully.", "data": serializer.data},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
