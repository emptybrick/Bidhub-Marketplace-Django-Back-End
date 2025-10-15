from django.db import models
from django.core.validators import MinValueValidator

class Bid(models.Model):
    user_id = models.ForeignKey(related_name="bids")
    bid = models.DecimalField(blank=False, null=False, max_digits=10,
                              decimal_places=2, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)