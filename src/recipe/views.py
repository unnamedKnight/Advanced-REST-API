from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import Recipe
from .serializers import RecipeSerializer, RecipeDetailsSerializer

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
        # here self.acton means the operations we can perform using ModelSerializer
        # for example ['list', 'retrieve', 'create', 'update', 'destroy']
        # if self.action == "list":
        #     return RecipeSerializer
        # return self.serializer_class
        # another implementation of the if self.action == 'list' expression
        return RecipeSerializer if self.action == "list" else self.serializer_class


