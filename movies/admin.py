from django.contrib import admin

from .models import Category, Film, Genre


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ("title", "year", "category", "genre_list")
    search_fields = ("title", "description", "category__name", "genre__name")
    list_filter = ("category", "year")

    def genre_list(self, obj):
        return ", ".join(g.name for g in obj.genre.all())

    genre_list.short_description = "Genres (M2M)"


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
