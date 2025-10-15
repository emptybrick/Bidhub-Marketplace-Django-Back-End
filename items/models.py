from django.db import models
from common.utils import Item_Categories
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime
from django.utils import timezone

class Item(models.Model):
    item_name = models.CharField(max_length=80, blank=False, null=False)
    owner = models.ForeignKey(
        "authentication.User",
        related_name="items",
        on_delete=models.CASCADE
    )
    category = Item_Categories.choices()
    condition = models.CharField(max_length=4, choices=[(
        'USED', 'Used'), ('NEW', 'New')], default='NEW', blank=False, null=False)
    manufacture_year = models.IntegerField(max_length=4, validators=[
                                           MinValueValidator(1), MaxValueValidator(datetime.now().year)])
    country_of_origin = models.CharField(max_length=40)
    height = models.DecimalField(blank=False, null=False, max_digits=6,
                                 decimal_places=2, validators=[MinValueValidator(0.01)])
    width = models.DecimalField(blank=False, null=False, max_digits=6,
                                decimal_places=2, validators=[MinValueValidator(0.01)])
    length = models.DecimalField(blank=False, null=False, max_digits=6,
                                 decimal_places=2, validators=[MinValueValidator(0.01)])
    weight = models.DecimalField(blank=False, null=False, max_digits=6,
                                 decimal_places=2, validators=[MinValueValidator(0.01)])
    description = models.TextField(blank=False, null=False)
    initial_bid = models.DecimalField(
        blank=False, null=False, max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    current_bid = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(blank=False, null=False)
    bid_history = models.ForeignKey(
        "bids.Bid", related_name='items', on_delete=models.CASCADE)
    final_bidder = models.ForeignKey("authentication.User", related_name='items')
    created_at = models.DateTimeField(auto_now_add=True)
    # images = models.JSONField(default=list, blank=True) # on hold

    # duration = models.DurationField(blank=False, null=False) # duration, probably drop and only use end_time
    # buy_now = models.DecimalField(max_digits=10,
    #                               decimal_places=2, validators=[MinValueValidator(0.01)]) # buy now stretch goal wth make offer? (dont want to lean into ecommerce to heavily)
