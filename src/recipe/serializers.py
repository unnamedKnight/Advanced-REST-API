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

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed."""
        authenticated_user = self.context["request"].user
        for tag in tags:
            # by passing tag as **tag, we are passing all the fields of tag
            # an example of passing **tag is
            #tag_obj, created = Tag.objects.get_or_create(user=authenticated_user, **tag)

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

    def create(self, validated_data):
        """Create a Recipe"""
        # removing tag from validated data
        tags = validated_data.pop("tags", [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        # this is how we get the user obj in serializer
        # HERE, context is passed to the serializer by the view
        # authenticated_user = self.context["request"].user

        return recipe

    def update(self, instance, validated_data):
        """Update Recipe."""
        tags = validated_data.pop("tags", None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

        # return super().update(instance, validated_data)


class RecipeDetailsSerializer(RecipeSerializer):
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ["description"]
