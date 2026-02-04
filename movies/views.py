from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .models import Category, Film, Genre


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
    # ORM: select_related + prefetch_related + order_by + filter
    films_qs = (
        Film.objects.select_related("category")
        .prefetch_related("genre")
        .order_by("title")
    )

    # query params (поддержим оба варианта: category и category_id)
    category_id_raw = request.GET.get("category") or request.GET.get("category_id")
    genre_id_raw = request.GET.get("genre") or request.GET.get("genre_id")
    q = (request.GET.get("q") or "").strip()

    selected_category_id = None
    selected_genre_id = None

    if q:
        films_qs = films_qs.filter(title__icontains=q)

    if category_id_raw:
        try:
            selected_category_id = int(category_id_raw)
            films_qs = films_qs.filter(category_id=selected_category_id)
        except ValueError:
            selected_category_id = None

    if genre_id_raw:
        try:
            selected_genre_id = int(genre_id_raw)
            films_qs = films_qs.filter(genre__id=selected_genre_id).distinct()
        except ValueError:
            selected_genre_id = None

    categories = Category.objects.order_by("name")
    genres = Genre.objects.order_by("name")

    # ORM: count + slicing
    total_films = films_qs.count()
    latest_films = Film.objects.order_by("-id")[:5]

    return render(
        request,
        "movies/film_list.html",
        context={
            "films": films_qs,
            "categories": categories,
            "genres": genres,
            "selected_category_id": selected_category_id,
            "selected_genre_id": selected_genre_id,
            "q": q,
            "total_films": total_films,
            "latest_films": latest_films,
        },
    )


def film_detail(request, film_id: int):
    # ORM: get / 404
    film = get_object_or_404(
        Film.objects.select_related("category").prefetch_related("genre"),
        id=film_id,
    )

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


def film_create(request):
    """Создание фильма через внешний интерфейс (GET/POST + CSRF)."""

    if request.method == "GET":
        categories = Category.objects.order_by("name")
        genres = Genre.objects.order_by("name")
        return render(
            request,
            "movies/film_create.html",
            context={"categories": categories, "genres": genres},
        )

    # POST
    title = (request.POST.get("title") or "").strip()
    year_raw = (request.POST.get("year") or "").strip()
    description = (request.POST.get("description") or "").strip()
    category_id_raw = request.POST.get("category") or request.POST.get("category_id")
    genre_ids = request.POST.getlist("genre") or request.POST.getlist("genre_id")
    image = request.FILES.get("image")

    errors = []
    year = None
    if not title:
        errors.append("Введите название фильма.")
    try:
        year = int(year_raw)
    except (TypeError, ValueError):
        errors.append("Введите корректный год (число).")

    category_obj = None
    if category_id_raw:
        try:
            category_obj = Category.objects.get(id=int(category_id_raw))
        except (ValueError, Category.DoesNotExist):
            category_obj = None

    if errors:
        categories = Category.objects.order_by("name")
        genres = Genre.objects.order_by("name")
        return render(
            request,
            "movies/film_create.html",
            context={
                "categories": categories,
                "genres": genres,
                "errors": errors,
                "form_data": {
                    "title": title,
                    "year": year_raw,
                    "description": description,
                    "category_id": category_id_raw or "",
                    "genre_ids": set(genre_ids),
                },
            },
        )

    film = Film.objects.create(
        title=title,
        year=year,
        category=category_obj,
        description=description,
        image=image,
    )

    # Привязываем жанры (ManyToMany)
    if genre_ids:
        valid_ids = []
        for g in genre_ids:
            try:
                valid_ids.append(int(g))
            except ValueError:
                continue
        if valid_ids:
            film.genre.set(Genre.objects.filter(id__in=valid_ids))

    return redirect(f"/movies/{film.id}/")
