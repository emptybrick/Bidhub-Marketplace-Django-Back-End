from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    rating = models.DecimalField(blank=True, null=True, max_digits=3,
                                 decimal_places=2, validators=[MinValueValidator(0.01)])
    seller_id = models.ForeignKey(
        'authentication.User', related_name="reviews", on_delete=models.CASCADE)
    author = models.ForeignKey(
        "authentication.User", related_name="reviews")
    review = models.TextField(blank=False, null=False)
    service_rating = models.IntegerField(null=False, blank=False, validators=[
                                         MinValueValidator(1), MaxValueValidator(10)])
    product_rating = models.IntegerField(null=False, blank=False, validators=[
                                         MinValueValidator(1), MaxValueValidator(10)])
    packaging_rating = models.IntegerField(null=False, blank=False, validators=[
                                           MinValueValidator(1), MaxValueValidator(10)])
    shipping_rating = models.IntegerField(null=False, blank=False, validators=[
                                          MinValueValidator(1), MaxValueValidator(10)])
    overall_rating = models.IntegerField(null=False, blank=False, validators=[
                                         MinValueValidator(1), MaxValueValidator(10)])
    created_at = models.DateTimeField(auto_now_add=True)
