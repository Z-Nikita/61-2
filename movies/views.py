from django.db.models import Count
from django.shortcuts import get_object_or_404, render

from .models import Category, Film


def home(request):
    # ORM: annotate
    categories = (
        Category.objects.annotate(film_count=Count("films"))
        .order_by("name")
    )

    return render(
        request,
        "movies/home.html",
        context={"categories": categories},
    )


def film_list(request):
    # ORM: select_related + order_by + filter
    films_qs = Film.objects.select_related("category").order_by("title")

    category_id = request.GET.get("category")
    selected_category_id = None

    if category_id:
        try:
            selected_category_id = int(category_id)
            films_qs = films_qs.filter(category_id=selected_category_id)
        except ValueError:
            selected_category_id = None

    categories = Category.objects.order_by("name")

    # ORM: count + slicing
    total_films = films_qs.count()
    latest_films = Film.objects.order_by("-id")[:5]

    return render(
        request,
        "movies/film_list.html",
        context={
            "films": films_qs,
            "categories": categories,
            "selected_category_id": selected_category_id,
            "total_films": total_films,
            "latest_films": latest_films,
        },
    )


def film_detail(request, film_id: int):
    # ORM: get / 404
    film = get_object_or_404(Film.objects.select_related("category"), id=film_id)

    categories = Category.objects.order_by("name")

    # ORM: показать похожие фильмы
    similar_films = []
    if film.category_id:
        similar_films = (
            Film.objects.filter(category_id=film.category_id)
            .exclude(id=film.id)
            .order_by("title")[:5]
        )

    return render(
        request,
        "movies/film_detail.html",
        context={
            "film": film,
            "categories": categories,
            "similar_films": similar_films,
        },
    )
