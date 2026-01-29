from django.contrib import admin

from .models import Film


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ("title", "year", "genre")
    search_fields = ("title", "genre")
    list_filter = ("genre", "year")
