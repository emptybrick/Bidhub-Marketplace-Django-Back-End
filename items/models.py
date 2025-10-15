from django.db import models

# Create your models here.


class Item(models.Model):
    def __str__(self):
        return f'{self.title} - {self.author}'

    # models.CharField is the data type and means "string"
    title = models.CharField(max_length=80, unique=True)
    author = models.ForeignKey(
        "authentication.User",
        related_name="created_items",
        on_delete=models.CASCADE
    )

    genre = models.CharField(max_length=60)
    year = models.FloatField()
    owner = models.ForeignKey(
        "authentication.User",
        related_name="items",
        on_delete=models.CASCADE
    )
