from django.db import models
from users.models import Profile


class Category(models.Model):
    """Категория фильма (например: 12+, 16+, 18+ или любая группа)."""

    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.name


class Genre(models.Model):
    """Жанр фильма (ManyToMany)."""

    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name


class Film(models.Model):
    title = models.CharField(max_length=255)
    year = models.PositiveSmallIntegerField()

    # владелец фильма (Profile OneToOne -> Film ForeignKey)
    profile = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="films",
    )


    # изображение (фото постера)
    image = models.ImageField(null=True, blank=True, upload_to="films/")

    # жанры (ManyToMany) — поле переопределено по просьбе преподавателя
    genre = models.ManyToManyField(Genre, blank=True, related_name="films")

    # новая сущность "Категория"
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="films",
    )

    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.title} ({self.year})"
