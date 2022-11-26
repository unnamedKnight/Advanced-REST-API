from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

class Recipe(models.Model):

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    title = models.CharField(max_length=220)
    description = models.TextField(null=True, blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField("Tag")

    def __str__(self):
        return (f"{self.title} + {self.id}")


class Tag(models.Model):
    """Tags for filtering recipes"""
    title = models.CharField(max_length=50)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return self.title