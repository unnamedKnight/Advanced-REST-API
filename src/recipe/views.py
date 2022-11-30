from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import ListModelMixin, UpdateModelMixin, DestroyModelMixin

from .models import Recipe, Tag, Ingredient
from .serializers import (
    RecipeSerializer,
    RecipeDetailsSerializer,
    RecipeImageSerializer,
    TagSerializer,
    IngredientSerializer,
)

# Create your views here.


class RecipeViewSet(viewsets.ModelViewSet):
    """View for managing recipe APIs"""

    serializer_class = RecipeDetailsSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("-id")

    def get_serializer_class(self):
        """Returns the serializer class for request"""
        # here self.action means the operations we can perform using ModelSerializer
        # for example ['list', 'retrieve', 'create', 'update', 'destroy']
        if self.action == "list":
            return RecipeSerializer
        elif self.action == "upload_image":
            return RecipeImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new Recipe"""
        serializer.save(user=self.request.user)
        # return super().perform_create(serializer)

    # here we added a custom action with the help of action decorator
    # now we can access this action with self.action
    # and here detail=True means this action going to work
    # with a single instance of the Recipe model
    # which means we need a pk to access this action
    # and url_path defines the custom url path in the router for the action
    @action(methods=["POST"], detail=True, url_path="upload_image")
    def upload_image(self, request, pk=None):
        """Upload an image to recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseRecipeAttrViewSet(
    DestroyModelMixin, UpdateModelMixin, ListModelMixin, viewsets.GenericViewSet
):
    """BaseViewSet for Recipe attributes"""

    # we haven't added CreateModelMixin so we cannot perform
    # post method in this base class
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database"""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()

    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user).order_by("-title")


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database."""

    # UpdateModelMixin checks if the current user is the owner of the
    # model instance automatically

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()

    def get_queryset(self):
        """Filter queryset to authenticate user."""
        return self.queryset.filter(user=self.request.user).order_by("-name")
