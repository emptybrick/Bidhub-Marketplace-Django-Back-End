from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Q, Count, Max, F, ExpressionWrapper, DurationField
from datetime import timedelta

from .models import Item
from .serializers.common import ItemSerializer
from .serializers.populated import PopulatedItemSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class ItemPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50

class ItemListView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = ItemPagination

    def get(self, request):
        """Get filtered list of items with comprehensive search options"""
        # Create base queryset
        items = Item.objects.all()

        # Basic filtering
        category = request.query_params.get('category')
        if category:
            items = items.filter(category=category)

        # Price range filtering
        min_price = request.query_params.get('min_price')
        if min_price and min_price.isdigit():
            items = items.filter(starting_price__gte=float(min_price))

        max_price = request.query_params.get('max_price')
        if max_price and max_price.isdigit():
            items = items.filter(starting_price__lte=float(max_price))

        # Text search
        search_term = request.query_params.get('search')
        if search_term:
            items = items.filter(
                Q(title__icontains=search_term) |
                Q(description__icontains=search_term)
            )

        # Auction status filtering
        auction_status = request.query_params.get('status')
        now = timezone.now()
        if auction_status == 'active':
            items = items.filter(Q(auction_end__gt=now) |
                                 Q(auction_end__isnull=True))
        elif auction_status == 'ended':
            items = items.filter(auction_end__lte=now)
        elif auction_status == 'ending_soon':
            items = items.filter(auction_end__gt=now,
                                 auction_end__lt=now + timedelta(hours=24))

        # Condition filtering
        condition = request.query_params.get('condition')
        if condition:
            items = items.filter(condition=condition)

        # Add bid information via annotation
        items = items.annotate(
            bid_count=Count('bids'),
            highest_bid=Max('bids__amount')
        )

        # Sorting
        sort_by = request.query_params.get('sort', 'created_at')
        valid_sort_fields = ['created_at', 'starting_price',
                             'auction_end', 'highest_bid', 'bid_count']

        if sort_by not in valid_sort_fields:
            sort_by = 'created_at'

        # Handle special sort cases
        if sort_by == 'time_remaining' and auction_status != 'ended':
            # Sort by time left in auction
            items = items.filter(auction_end__isnull=False)
            items = items.annotate(
                time_left=ExpressionWrapper(
                    F('auction_end') - timezone.now(), output_field=DurationField())
            )
            sort_by = 'time_left'

        # Apply sort direction
        sort_dir = request.query_params.get('direction', 'desc').lower()
        if sort_dir == 'desc' and sort_by != 'time_left':
            sort_by = f'-{sort_by}'
        elif sort_dir == 'asc' and sort_by == 'time_left':
            # Invert for time_left to make "ending soon" first
            sort_by = f'-{sort_by}'

        items = items.order_by(sort_by)

        # Apply pagination
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(items, request)

        # Use populated serializer if detailed=true is requested
        if request.query_params.get('detailed') == 'true':
            serialized_items = PopulatedItemSerializer(page, many=True)
        else:
            serialized_items = ItemSerializer(page, many=True)

        return paginator.get_paginated_response(serialized_items.data)

    def post(self, request):
        """Create a new item"""
        request.data["owner"] = request.user.id
        item_to_add = ItemSerializer(data=request.data)

        try:
            item_to_add.is_valid(raise_exception=True)
            item_to_add.save()
            return Response(item_to_add.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(e.__dict__ if hasattr(e, '__dict__') else str(e),
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)

class ItemDetailView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_item(self, pk):
        """Helper method to get an item by ID"""
        try:
            return Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            raise NotFound(detail="Item not found")

    def get(self, request, pk):
        """Get a specific item with auction status and bid information"""
        item = self.get_item(pk=pk)  # Use helper method

        # Get related items (same category or owner)
        related_items = Item.objects.filter(
            Q(category=item.category) | Q(owner=item.owner)
        ).exclude(pk=pk)[:5]  # Limit to 5 items

        serialized_item = PopulatedItemSerializer(item)
        data = serialized_item.data

        # Auction status information
        now = timezone.now()
        data['auction_active'] = True if not item.auction_end or item.auction_end > now else False

        if item.auction_end:
            if item.auction_end > now:
                # Calculate time remaining and format it
                time_remaining = item.auction_end - now
                days, remainder = divmod(time_remaining.total_seconds(), 86400)
                hours, remainder = divmod(remainder, 3600)
                minutes = divmod(remainder, 60)[0]

                data['time_remaining'] = {
                    'days': int(days),
                    'hours': int(hours),
                    'minutes': int(minutes),
                    'total_seconds': time_remaining.total_seconds()
                }
            else:
                data['time_remaining'] = None

        # Bid information
        from bids.models import Bid
        bids = Bid.objects.filter(item=item)
        data['bid_count'] = bids.count()

        highest_bid = bids.order_by('-amount').first()
        if highest_bid:
            data['highest_bid'] = highest_bid.amount
            data['highest_bidder'] = highest_bid.bidder.id
        else:
            data['highest_bid'] = None
            data['highest_bidder'] = None

        # Related items
        data['related_items'] = ItemSerializer(related_items, many=True).data

        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """Update an item"""
        item_to_update = self.get_item(pk=pk)

        if item_to_update.owner.id != request.user.id:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

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

    def delete(self, request, pk):
        """Delete an item"""
        item_to_delete = self.get_item(pk=pk)

        if item_to_delete.owner.id != request.user.id:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        # Checking if there are bids before allowing deletion
        from bids.models import Bid
        if Bid.objects.filter(item=item_to_delete).exists():
            return Response(
                {"detail": "Cannot delete item with existing bids"},
                status=status.HTTP_400_BAD_REQUEST
            )

        item_to_delete.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
