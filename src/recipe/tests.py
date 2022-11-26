from django.test import TestCase

from decimal import Decimal
from core import models
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from .models import Recipe, Tag
from .serializers import RecipeSerializer, RecipeDetailsSerializer

# Create your tests here.


RECIPE_LIST = reverse("recipe:recipe-list")


def detail_url(recipe_id):
    "Create and return a recipe detail URL."
    # return reverse('recipe:recipe-detail', args=(recipe_id,))
    return reverse("recipe:recipe-detail", kwargs={"pk": recipe_id})


def create_user(email="user@example.com", password="password123"):
    user = get_user_model().objects.create(email=email, password=password)
    user.set_password(user.password)
    return user



def create_recipe(user, **params):  # sourcery skip: dict-assign-update-to-union
    """Create and return a recipe"""
    defaults = {
        "title": "Sample recipe title",
        "time_minutes": 22,
        "price": Decimal("5.25"),
        "description": "Sample recipe description",
        "link": "http://example.com/recipe.pdf",
    }
    defaults.update(params)

    # recipe = Recipe.objects.create(user=user, **defaults)
    return Recipe.objects.create(user=user, **defaults)

    # def test_create_recipe(self):
    #     recipe = Recipe.objects.create(
    #         user=self.user,
    #         title="Sample recipe title",
    #         time_minutes=5,
    #         price=Decimal("5.50"),
    #         description="Sample recipe description",
    #     )
    #     self.assertAlmostEqual(str(recipe), recipe.title)


class PublicRecipeAPITests(TestCase):
    "Test unauthenticated API requests."

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        "Test auth is required to call API"
        response = self.client.get(RECIPE_LIST)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            email="user@example.com",
            password="password123",
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        response = self.client.get(RECIPE_LIST)

        recipes = Recipe.objects.all().order_by("-id")
        serializers = RecipeSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializers.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail"""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        response = self.client.get(url)
        serializer = RecipeDetailsSerializer(recipe)
        self.assertEqual(response.data, serializer.data)

    def test_create_recipe(self):
        """Test creating recipe"""
        payload = {
            "title": "Sample recipe title",
            "time_minutes": 22,
            "price": Decimal("5.25"),

        }
        response = self.client.post(RECIPE_LIST, payload)
        recipe = Recipe.objects.get(id=response.data.get('id'))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key, value in payload.items():
            # comparing the value of recipe with the key of payload
            self.assertEqual((getattr(recipe, key)), value)
        self.assertEqual(recipe.user, self.user)



class TagAPITests(TestCase):

    def setUp(self) -> None:
        self.user = create_user()
        self.client = APIClient()

    def test_create_tag(self):
        title = "example tag1"
        user = self.user
        tag = Tag.objects.create(user=user, title=title)
        self.assertEqual(tag.title, title)

