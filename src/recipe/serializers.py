from rest_framework import serializers

from .models import Recipe, Tag, Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name")
        read_only_fields = ("id",)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "title")
        read_only_fields = ("id",)


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ["id", "title", "time_minutes", "price", "link", "tags", "ingredients"]
        read_only_fields = ["id"]

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed."""
        authenticated_user = self.context["request"].user
        for tag in tags:
            # by passing tag as **tag, we are passing all the fields of tag
            # an example of passing **tag is
            # tag_obj, created = Tag.objects.get_or_create(user=authenticated_user, **tag)

            # but this is case sensitive
            # which means if there are two tags with the same title
            # for example, lunch and Lunch. this will create two different tags
            # and we want to avoid this type of behavior
            # we can achieve this by doing the following
            # here we are using get_or_create, and filtering by __icontains
            # if a tag exists it will return that tag, if not it will create a new tag
            # based on the default value
            # if we don't provide a default value it will create an empty tag

            tag_obj, created = Tag.objects.get_or_create(
                defaults={"title": tag["title"]},
                user=authenticated_user,
                title__icontains=tag["title"],
            )

            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, recipe):
        """Handle getting or creating ingredients as needed."""
        authenticated_user = self.context["request"].user
        for ingredient in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(
                defaults={"name": ingredient["name"]},
                user=authenticated_user,
                name__icontains=ingredient["name"],
            )

            recipe.ingredients.add(ingredient_obj)

    def create(self, validated_data):
        """Create a Recipe"""
        # removing tag from validated data
        tags = validated_data.pop("tags", [])
        ingredients = validated_data.pop("ingredients", [])
        # lower casing ingredients name
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)
        # this is how we get the user obj in serializer
        # HERE, context is passed to the serializer by the view
        # authenticated_user = self.context["request"].user

        return recipe

    def update(self, instance, validated_data):
        """Update Recipe."""
        tags = validated_data.pop("tags", None)
        ingredients = validated_data.pop("ingredients", None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

        # return super().update(instance, validated_data)


class RecipeDetailsSerializer(RecipeSerializer):
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ["description"]


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes."""

    class Meta:
        model = Recipe
        fields = ["id", "image"]
        read_only_fields = ["id"]
        extra_kwargs = {"image": {"required": True}}
