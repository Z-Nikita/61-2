from django.contrib import admin

from .models import Category, Film


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ("title", "year", "category", "genre")
    search_fields = ("title", "genre", "description")
    list_filter = ("category", "year")
