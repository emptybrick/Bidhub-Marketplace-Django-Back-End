from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    rating = models.DecimalField(
        blank=True,
        null=True,
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(1)]
    )
    seller_id = models.ForeignKey(
        'authentication.User',
        related_name="seller_reviews",
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        "authentication.User",
        related_name="reviews",
        on_delete=models.SET_NULL,
        null=True
    )
    review = models.TextField(
        blank=False,
        null=False
    )
    service_rating = models.IntegerField(
        null=False,
        blank=False,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    product_rating = models.IntegerField(
        null=False,
        blank=False,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    packaging_rating = models.IntegerField(
        null=False,
        blank=False,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    shipping_rating = models.IntegerField(
        null=False,
        blank=False,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    overall_rating = models.IntegerField(
        null=False,
        blank=False,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
