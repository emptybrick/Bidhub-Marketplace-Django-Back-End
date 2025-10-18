from django.db import models
from django.core.validators import MinValueValidator


class Bid(models.Model):
    bid = models.DecimalField(
        blank=False,
        null=False,
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(1.00)]
    )
    user_id = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        related_name="bids",
        blank=True,
        null=True
    )
    item_id = models.ForeignKey(
        'items.Item',
        related_name="bids",
        on_delete=models.PROTECT,
        blank=True,
        null=True  # if item is deleted, delete all associated bids too
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
