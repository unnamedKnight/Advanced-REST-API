# Generated by Django 4.1.3 on 2022-11-26 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipe", "0002_alter_recipe_time_minutes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipe",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
    ]