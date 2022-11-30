from django.db import models
from django.contrib.auth import get_user_model
import uuid
import os

# Create your models here.

def recipe_image_file_path(instance, filename):
    # here instance refers to an instance of the Recipe Model
    """Generate file path for new recipe image."""
    # with the following statement
    # we are removing the extension from the filename
    # splitext is a function of path module
    # which extracts the extension of a given filename
    ext = os.path.splitext(filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    return os.path.join("uploads", "recipe", filename)


class Recipe(models.Model):

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    title = models.CharField(max_length=220)
    description = models.TextField(null=True, blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField("Tag")
    ingredients = models.ManyToManyField("Ingredient")
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self):
        return (f"{self.title} -----> {self.id}")


class Tag(models.Model):
    """Tags for filtering recipes"""
    title = models.CharField(max_length=50)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    """Ingredient for Recipes."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)


    def __str__(self):
        return self.name