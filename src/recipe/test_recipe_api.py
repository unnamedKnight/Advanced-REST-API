from django.test import TestCase
import tempfile
import os

from PIL import Image

from decimal import Decimal
from core import models
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

def image_upload_url(recipe_id):
    """Create and return an image upload URL."""
    return reverse("recipe:recipe-upload-image", args=[recipe_id])


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
    """Test unauthenticated API requests."""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        "Test auth is required to call API"
        response = self.client.get(RECIPE_LIST)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test authenticated API requests"""

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
        recipe = Recipe.objects.get(id=response.data.get("id"))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key, value in payload.items():
            # comparing the value of recipe with the key of payload
            self.assertEqual((getattr(recipe, key)), value)
        self.assertEqual(recipe.user, self.user)

    def test_create_recipe_with_new_tags(self):
        """Test creating a new recipe with new tags."""
        payload = {
            "title": "Thai prawn curry",
            "time_minutes": 30,
            "price": Decimal("8.25"),
            "tags": [{"title": "Thai"}, {"title": "Dinner"}],
        }
        response = self.client.post(RECIPE_LIST, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

    def test_create_recipe_with_existing_tags(self):
        """Test creating a new recipe with existing tags."""
        tag_indian = Tag.objects.create(user=self.user, title="Indian")
        payload = {
            "title": "Pongal",
            "time_minutes": 60,
            "price": Decimal("4.50"),
            "tags": [{"title": "Indian"}, {"title": "Breakfast"}],
        }

        response = self.client.post(RECIPE_LIST, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())

    def test_create_tag_on_update(self):
        """Test creating tag when updating a recipe."""
        recipe = create_recipe(user=self.user)

        payload = {"tags": [{"title": "Lunch"}]}
        url = detail_url(recipe.id)
        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, title="Lunch")
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """Test assigning an existing tag when updating a recipe."""
        tag_breakfast = Tag.objects.create(user=self.user, title="Breakfast")
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, title="Lunch")
        payload = {"tags": [{"title": "Lunch"}]}

        url = detail_url(recipe.id)
        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_create_recipe_with_new_ingredients(self):
        """Test creating new recipe with new ingredients."""
        payload = {
            "title": "Cauliflower Tacos",
            "time_minutes": 60,
            "price": Decimal("4.30"),
            "ingredients": [{"name": "Cauliflower"}, {"name": "Salt"}],
        }
        response = self.client.post(RECIPE_LIST, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        for ingredient in payload["ingredients"]:
            exists = recipe.ingredients.filter(
                name=ingredient["name"], user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredients(self):
        """Test creating new recipe with new ingredients."""

        ingredient = Ingredient.objects.create(user=self.user, name="Lemon")
        payload = {
            "title": "Vietnamese Soup",
            "time_minutes": 25,
            "price": Decimal("4.30"),
            "ingredients": [{"name": "Lemon"}, {"name": "Fish Sauce"}],
        }

        response = self.client.post(RECIPE_LIST, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingredient, recipe.ingredients.all())

    def test_create_ingredient_on_update(self):
        """Test creating ingredient on update."""
        recipe = create_recipe(user=self.user)
        payload = {"ingredients": [{"name": "Limes"}]}
        url = detail_url(recipe.id)
        response = self.client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertIn("Limes", recipe.ingredients.all())

    def test_update_recipe_assign_ingredient(self):
        """Test assigning an existing ingredient when updating a recipe."""
        ingredient1=Ingredient.objects.create(user=self.user, name="Pepper")
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient1)
        ingredient2=Ingredient.objects.create(user=self.user, name="Chili")
        payload = {"ingredients": [{"name": "Chili"}]}
        url = detail_url(recipe.id)
        response = self.client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient2, recipe.ingredients.all())


class ImageUploadTests(TestCase):
    """Tests for the image upload API."""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)


    def tearDown(self) -> None:
        self.recipe.image.delete()


    def test_upload_image(self):
        """Test uploading an image to a recipe."""

        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = Image.new("RGB", (10, 10))
            img.save(image_file, format="JPEG")
            image_file.seek(0)
            payload = {"image": image_file}
            response = self.client.post(url, payload, format="multipart")
        self.recipe.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("image", response.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))