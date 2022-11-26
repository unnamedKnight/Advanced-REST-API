from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import ListModelMixin, UpdateModelMixin, DestroyModelMixin

from .models import Recipe, Tag
from .serializers import RecipeSerializer, RecipeDetailsSerializer, TagSerializer

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
        # if self.action == "list":
        #     return RecipeSerializer
        # return self.serializer_class
        # another implementation of the above if self.action == 'list' expression is
        return RecipeSerializer if self.action == "list" else self.serializer_class

    def perform_create(self, serializer):
        """Create a new Recipe"""
        serializer.save(user=self.request.user)
        # return super().perform_create(serializer)


class TagViewSet(
    DestroyModelMixin, UpdateModelMixin, ListModelMixin, viewsets.GenericViewSet
):
    """Manage tags in the database"""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user).order_by("-title")
