from rest_framework import serializers

from .models import Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "title")
        read_only_fields = ("id",)


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ["id", "title", "time_minutes", "price", "link", "tags"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        """Create a Recipe"""
        # removing tag from validated data
        tags = validated_data.pop("tags", [])
        recipe = Recipe.objects.create(**validated_data)
        # this is how we get the user obj in serializer
        # HERE, context is passed to the serializer by the view
        authenticated_user = self.context["request"].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=authenticated_user, **tag
            )
            recipe.tags.add(tag_obj)

        return recipe


class RecipeDetailsSerializer(RecipeSerializer):
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ["description"]
