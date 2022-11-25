from django.test import TestCase

from decimal import Decimal
from core import models
from django.contrib.auth import get_user_model

# Create your tests here.

class ModelTests(TestCase):

    def create_user(self):
        username = "user@example.com"
        password = "password123"
        user = get_user_model().objects.create(
            email=username, password=password
        )
        user.set_password(user.password)
        self.user = user


    def setUp(self) -> None:
        self.create_user()

    def test_create_recipe(self):
        recipe = models.Recipe.objects.create(
            user=self.user,
            title="Sample recipe title",
            time_minutes=5,
            price=Decimal('5.50'),
            description="Sample recipe description"
        )
        self.assertAlmostEqual(str(recipe), recipe.title)
