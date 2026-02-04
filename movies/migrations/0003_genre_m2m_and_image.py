# Generated manually (compatible with Django 5.x)
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("movies", "0002_category_and_film_category"),
    ]

    operations = [
        # 1) Переименуем старое текстовое поле жанра
        migrations.RenameField(
            model_name="film",
            old_name="genre",
            new_name="genre_text",
        ),
        # 2) Добавим отдельную сущность Genre
        migrations.CreateModel(
            name="Genre",
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
                ("name", models.CharField(max_length=255, unique=True)),
            ],
        ),
        # 3) Поле изображения (постер)
        migrations.AddField(
            model_name="film",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="films/"),
        ),
        # 4) Переопределяем genre как ManyToMany
        migrations.AddField(
            model_name="film",
            name="genre",
            field=models.ManyToManyField(
                blank=True,
                related_name="films",
                to="movies.genre",
            ),
        ),
    ]
