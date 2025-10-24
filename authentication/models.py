from django.db import models
# user model that already exists in django
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal

class User(AbstractUser):  # we extend the AbstractUser and add the fields that we want for our users
    username = models.CharField(
        max_length=24,
        blank=False,
        null=False,
        unique=True
    )
    email = models.EmailField(
        max_length=254,
        blank=False,
        null=False,
        unique=True
    )
    first_name = models.CharField(
        max_length=50,
        blank=False,
        null=False
    )
    last_name = models.CharField(
        max_length=50,
        blank=False,
        null=False
    )
    user_rating = models.DecimalField(
        blank=True,
        null=True,
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    favorites = models.JSONField(
        default=list, blank=True, null=True)
    
    profile_image = models.CharField(blank=True, null=True)
    
    items_sold = models.IntegerField(blank=True, null=True)

    date_joined = models.DateTimeField(auto_now_add=True)

    def add_favorite(self, item_id):
        """Add item_id to favorites if not already present"""
        if self.favorites is None:
            self.favorites = []
        if item_id not in self.favorites:
            self.favorites.append(item_id)
            self.save(update_fields=['favorites'])

    def remove_favorite(self, item_id):
        """Remove item_id from favorites"""
        if self.favorites and item_id in self.favorites:
            self.favorites.remove(item_id)
            self.save(update_fields=['favorites'])

    def toggle_favorite(self, item_id):
        """Toggle item_id in favorites"""
        if item_id in self.favorites:
            self.remove_favorite(item_id)
        else:
            self.add_favorite(item_id)

    def is_favorited(self, item_id):
        """Check if item is favorited"""
        return bool(self.favorites and item_id in self.favorites)


class BlackListedToken(models.Model):
    token = models.CharField(max_length=500)
    blacklisted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Blacklisted: {self.blacklisted_at}"