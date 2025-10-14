from django.db import models
from django.contrib.auth.models import AbstractUser # user model that already exists in django

class User(AbstractUser): # we extend the AbstractUser and add the fields that we want for our users
    email = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    profile_image = models.CharField(max_length=300)