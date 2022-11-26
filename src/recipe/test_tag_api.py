from django.test import TestCase

from core import models
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from .models import Recipe, Tag
from .serializers import RecipeSerializer, RecipeDetailsSerializer, TagSerializer


TAG_URL = reverse("recipe:tag-list")


def detail_url(recipe_id):
    "Create and return a recipe detail URL."
    # return reverse('recipe:recipe-detail', args=(recipe_id,))
    return reverse("recipe:recipe-detail", kwargs={"pk": recipe_id})


def create_user(email="user@example.com", password="password123"):
    user = get_user_model().objects.create(email=email, password=password)
    user.set_password(user.password)
    return user


class PublicTagAPITests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self) -> None:
        self.user = create_user()
        self.client = APIClient()

    def test_create_tag(self):
        title = "example tag1"
        user = self.user
        tag = Tag.objects.create(user=user, title=title)
        self.assertEqual(tag.title, title)

    def test_auth_required(self):
        response = self.client.get(TAG_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagAPITests(TestCase):
    """Test authenticated API requests"""

    def setUp(self) -> None:
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        Tag.objects.create(user=self.user, title="Vegan")
        Tag.objects.create(user=self.user, title="Desert")

        response = self.client.get(TAG_URL)
        tags = Tag.objects.all().order_by("-title")
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test list of tags is limited to authenticated users"""
        user2 = create_user(email="user2@example.com")
        Tag.objects.create(user=user2, title="Fruity")
        tag = Tag.objects.create(user=self.user, title="Comfort Food")

        response = self.client.get(TAG_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], tag.title)
