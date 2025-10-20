from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
# from django.utils import timezone
# from django.db.models import Q, Count, Max, F, ExpressionWrapper, DurationField
# from datetime import timedelta

from .models import Item
# from bids.models import Bid  # Import Bid from the correct app
from .serializers.common import ItemSerializer
from .serializers.populated import PopulatedItemSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from bids.serializer import BidSerializer

class ItemPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50

# need to add pagination to itemlist view


class ItemListView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = ItemPagination

    # GET All Items
    def get(self, request):
        """Get filtered list of items with comprehensive search options"""
        category = request.query_params.get('category', 'all') # Default to 'all'
        condition = request.query_params.get('condition', 'none')
        owner = request.query_params.get('owner', 'none') # logic to filter by seller/user when needed
        sort_by_end = request.query_params.get("end", 'none')
        sort_by_bid = request.query_params.get("bid", 'none')
        sort_by_start = request.query_params.get("start", 'none')
        print(condition)


        items = Item.objects.all() # Return all items
        
        if category != 'all':
            items = items.filter(category=category)
        if condition != "all":
            items = items.filter(condition=condition)
        if owner != "none":
            items = items.filter(owner.id==owner) # need to test

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

        # paginator = self.pagination_class()
        # page = paginator.paginate_queryset(items, request)
        # serializer = ItemSerializer(page, many=True)

        # return paginator.get_paginated_response(serializer.data)

        serialized_items = ItemSerializer(items, many=True)

        return Response(serialized_items.data, status=status.HTTP_200_OK)


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
    # both authenticated and unauthenticated users can view item details
    permission_classes = (IsAuthenticatedOrReadOnly,)

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

        # item.bid_history = getAll bids by bid.item_id then sort asc(highest bid first) then BidSerializer(item.bid_history)

        # Bid information
        # need to include bid.user_id to populate username and then only show first and last char with 3 *'s
        # bids = Bid.objects.filter(item=item)
        # data['bid_count'] = bids.count()

        # highest_bid = bids.order_by('-amount').first()
        # if highest_bid:
        #     data['highest_bid'] = highest_bid.amount
        #     data['highest_bidder'] = highest_bid.bidder.id
        # else:
        #     data['highest_bid'] = None
        #     data['highest_bidder'] = None

        # # Basic filtering
        # category = request.query_params.get('category')
        # if category:
        #     items = items.filter(category=category)

        # # Price range filtering
        # # filter by current bid - item.current_bid
        # min_price = request.query_params.get('min_price')
        # if min_price and min_price.isdigit():
        #     items = items.filter(starting_price__gte=float(min_price))

        # max_price = request.query_params.get('max_price')
        # if max_price and max_price.isdigit():
        #     items = items.filter(starting_price__lte=float(max_price))

        # # Text search
        # search_term = request.query_params.get('search')
        # if search_term:
        #     items = items.filter(
        #         Q(title__icontains=search_term) |
        #         Q(description__icontains=search_term)
        #     )

        # # Auction status filtering
        # # filter by item.end_time
        # # there is no logic for status currently need to create, auction is not used in models
        # auction_status = request.query_params.get('status')
        # now = timezone.now()
        # if auction_status == 'active':
        #     items = items.filter(Q(end_time__gt=now) |
        #                          Q(end_time__isnull=True))
        # elif auction_status == 'ended':
        #     items = items.filter(end_time__lte=now)
        # elif auction_status == 'ending_soon':
        #     items = items.filter(end_time__gt=now,
        #                          end_time__lt=now + timedelta(hours=24))

        # # Condition filtering
        # condition = request.query_params.get('condition')
        # if condition:
        #     items = items.filter(condition=condition)

        # # Add bid information via annotation
        # items = items.annotate(
        #     bid_count=Count('bids'),
        #     highest_bid=Max('bids__amount')
        # )

        # # Sorting
        # sort_by = request.query_params.get('sort', 'created_at')
        # # starting_price = initial_bid, end_time = end_time, highest_bid = current_bid
        # valid_sort_fields = ['created_at', 'starting_price',
        #                      'end_time', 'highest_bid', 'bid_count']

        # if sort_by not in valid_sort_fields:
        #     sort_by = 'created_at'

        # # Handle special sort cases
        # # there is no logic for time_remaining or status, auction is not used in models
        # # sort by end_time asc, desc
        # if sort_by == 'time_remaining' and auction_status != 'ended':
        #     # Sort by time left in auction
        #     items = items.filter(end_time__isnull=False)
        #     items = items.annotate(
        #         time_left=ExpressionWrapper(
        #             F('end_time') - timezone.now(), output_field=DurationField())
        #     )
        #     sort_by = 'time_left'

        # # Apply sort direction
        # sort_dir = request.query_params.get('direction', 'desc').lower()
        # if sort_dir == 'desc' and sort_by != 'time_left':
        #     sort_by = f'-{sort_by}'
        # elif sort_dir == 'asc' and sort_by == 'time_left':
        #     # Invert for time_left to make "ending soon" first
        #     sort_by = f'-{sort_by}'

        # items = items.order_by(sort_by)

        # # Apply pagination
        # paginator = self.pagination_class()
        # page = paginator.paginate_queryset(items, request)

        # Get related items (same category or owner)
        # why pull related items by category in detailed view
        # related_items = Item.objects.filter(Q(owner=item.owner)).exclude(pk=pk)[:5]  # Limit to 5 item

        # # Auction status information
        # now = timezone.now()
        # data['auction_active'] = True if not item.end_time or item.end_time > now else False

        # if item.end_time:
        #     if item.end_time > now:
        #         # Calculate time remaining and format it
        #         # we only want to show a relative end time, only show ends in 2 days 1 day, ends today
        #         time_remaining = item.end_time - now
        #         days, remainder = divmod(time_remaining.total_seconds(), 86400)
        #         hours, remainder = divmod(remainder, 3600)
        #         minutes = divmod(remainder, 60)[0]

        #         data['time_remaining'] = {
        #             'days': int(days),
        #             'hours': int(hours),
        #             'minutes': int(minutes),
        #             'total_seconds': time_remaining.total_seconds()
        #         }
        #     else:
        #         data['time_remaining'] = None

        # # Related items
        # data['related_items'] = ItemSerializer(related_items, many=True).data


#
