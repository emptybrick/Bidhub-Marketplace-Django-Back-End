from django.db import models

# Create your models here.


class Comment(models.Model):
    def __str__(self):
        return f'{self.text} - {self.Item}'

    text = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    Item = models.ForeignKey(
        "items.Item",
        related_name="comments",
        on_delete=models.CASCADE
    )
    owner = models.ForeignKey(  # if you call it user, I think it can clash with django fields so I tend to use owner
        "authentication.User",
        related_name="comments",
        on_delete=models.CASCADE,
    )
