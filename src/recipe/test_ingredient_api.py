from django.test import TestCase

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from .models import Recipe, Tag, Ingredient
from .serializers import (
    RecipeSerializer,
    RecipeDetailsSerializer,
    TagSerializer,
    IngredientSerializer,
)


INGREDIENT_URL = reverse("ingredient-list")


def detail_url(ingredient_id):
    "Create and return a recipe detail URL."
    # return reverse('recipe:recipe-detail', args=(recipe_id,))
    return reverse("recipe:ingredient-detail", kwargs={"pk": ingredient_id})


def create_user(email="user@example.com", password="password123"):
    user = get_user_model().objects.create(email=email, password=password)
    user.set_password(user.password)
    return user


class PublicIngredientAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving Ingredients"""
        response = self.client.get(INGREDIENT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITests(TestCase):
    """Test authenticated API requests"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving a list of ingredients."""
        Ingredient.objects.create(user=self.user, name="Kale")
        Ingredient.objects.create(user=self.user, name="Vanilla")

        response = self.client.get(INGREDIENT_URL)
        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test list of ingredients is limited to user"""
        user2 = create_user(email="user2@example.com")
        Ingredient.objects.create(user=user2, name="Salt")
        ingredient = Ingredient.objects.create(user=self.user, name="Pepper")

        response = self.client.get(INGREDIENT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], ingredient.name)
        self.assertEqual(response.data[0]["id"], ingredient.id)
