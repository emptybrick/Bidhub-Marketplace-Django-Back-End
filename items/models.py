from django.db import models
from common.utils import Item_Categories
from django.core.validators import MinValueValidator, MaxValueValidator
# from datetime import datetime
from django.utils import timezone


class Item(models.Model):
    item_name = models.CharField(
        max_length=80,
        blank=False,
        null=False
    )

    owner = models.ForeignKey(
        "authentication.User",
        related_name="items",
        on_delete=models.SET_NULL,
        null=True
    )
    category = models.CharField(choices=Item_Categories.choices(
    ), default=Item_Categories.MISCELLANEOUS.name, blank=False, null=False, db_index=True)
    condition = models.CharField(
        max_length=4,
        choices=[('USED', 'Used'), ('NEW', 'New')],
        default='NEW',
        blank=False,
        null=False,
        db_index=True
    )

    current_year = timezone.now().year
    manufacture_year = models.IntegerField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(1582),  # Gregorian calendar start year
            # Allow current year plus next year
            MaxValueValidator(current_year + 1)
        ],
        help_text="Enter a year between 1582 and the current year"
    )

    country_of_origin = models.CharField(max_length=40, blank=True, null=True)

    height = models.DecimalField(
        blank=False,
        null=False,
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0.01)])

    width = models.DecimalField(
        blank=False,
        null=False,
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0.01)])

    length = models.DecimalField(
        blank=False,
        null=False,
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0.01)])

    weight = models.DecimalField(
        blank=False,
        null=False,
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    description = models.TextField(
        blank=False,
        null=False
    )

    initial_bid = models.DecimalField(
        blank=False,
        null=False,
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    current_bid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        blank=True,
        null=True
    )

    start_time = models.DateTimeField(
        default=timezone.now
    )

    end_time = models.DateTimeField(
        blank=False,
        null=False,
        db_index=True
    )

    images = models.JSONField(default=list, blank=True, null=True)

    bid_history_json = models.JSONField(
        default=list, blank=True, null=True)

    highest_bidder = models.ForeignKey(
        "authentication.User",
        related_name="highest_bidder",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    payment_confirmation = models.CharField(
        max_length=20, blank=True, null=True)

    shipping_info = models.JSONField(
        default=dict, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
