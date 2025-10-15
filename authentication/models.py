from django.db import models
# user model that already exists in django
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinValueValidator

class User(AbstractUser):  # we extend the AbstractUser and add the fields that we want for our users
    username = models.CharField(max_length=24, blank=False, null=False)
    email = models.EmailField(max_length=254, blank=False, null=False)
    first_name = models.CharField(max_length=50, blank=False, null=False)
    last_name = models.CharField(max_length=50, blank=False, null=False)
    street_address = models.CharField(max_length=150, blank=False, null=False)
    city = models.CharField(max_length=40, blank=False, null=False)
    state = models.CharField(max_length=40, blank=False, null=False)
    postal_code = models.CharField(max_length=20, blank=False, null=False)
    country = models.CharField(max_length=100, blank=False, null=False)
    phone_number = PhoneNumberField(blank=False, null=False)
    wallet = models.DecimalField(blank=True, null=True, max_digits=12,
                                 decimal_places=2, validators=[MinValueValidator(0.01)])
    user_rating = models.DecimalField(blank=True, null=True, max_digits=3,
                                      decimal_places=2, validators=[MinValueValidator(0.01)])
