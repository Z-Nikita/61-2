# Generated manually (compatible with Django 5.x)
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Film",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("year", models.PositiveSmallIntegerField()),
                ("genre", models.CharField(blank=True, max_length=100)),
                ("description", models.TextField(blank=True)),
            ],
        ),
    ]
