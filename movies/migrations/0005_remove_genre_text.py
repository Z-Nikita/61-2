# Generated manually (compatible with Django 5.x)
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("movies", "0004_migrate_genre_text_to_m2m"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="film",
            name="genre_text",
        ),
    ]
