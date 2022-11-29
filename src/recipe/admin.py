from django.contrib import admin

from .models import Recipe, Tag, Ingredient

# Register your models here.

admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(Ingredient)