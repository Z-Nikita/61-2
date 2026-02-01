from django.db import models


class Category(models.Model):
    """Категория фильмов (например: Комедия, Драма, Боевик)."""

    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.name


class Film(models.Model):
    title = models.CharField(max_length=255)
    year = models.PositiveSmallIntegerField()
    genre = models.CharField(max_length=100, blank=True)

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
