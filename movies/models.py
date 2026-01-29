from django.db import models


class Film(models.Model):
    title = models.CharField(max_length=255)
    year = models.PositiveSmallIntegerField()
    genre = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.title} ({self.year})"
