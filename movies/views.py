from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CreateFilmForm, SearchFilmForm
from .models import Category, Film


def home(request):
    """Home page: categories with film counters."""

    categories = Category.objects.annotate(film_count=Count("films")).order_by("name")
    return render(request, "movies/home.html", context={"categories": categories})


@login_required(login_url="/login/")
def film_list(request):
    """Films list with search + filters.

    Required by assignment:
    - Search (поисковик)
    - Single-select filtering: dynamic (category) + static (year_choice)
    - Multi-select filtering: dynamic (genres M2M) + static (decades)
    """

    films_qs = Film.objects.select_related("category").prefetch_related("genre").order_by("title")

    # Backward compatibility with older query params from previous homework versions
    params = request.GET.copy()
    if params.get("q") and not params.get("search"):
        params["search"] = params.get("q")

    if params.get("category") and not params.get("category_id"):
        params["category_id"] = params.get("category")

    # single genre -> multi genres
    if params.get("genre") and not params.getlist("genres"):
        params.setlist("genres", [params.get("genre")])

    if params.get("genre_id") and not params.getlist("genres"):
        params.setlist("genres", [params.get("genre_id")])

    form = SearchFilmForm(params if params else None)

    if form.is_valid():
        search = (form.cleaned_data.get("search") or "").strip()
        if search:
            films_qs = films_qs.filter(Q(title__icontains=search) | Q(description__icontains=search))

        category = form.cleaned_data.get("category_id")
        if category:
            films_qs = films_qs.filter(category=category)

        # static single-choice filter
        year_choice = form.cleaned_data.get("year_choice")
        if year_choice:
            if year_choice == "1":
                films_qs = films_qs.filter(year__gte=2015)
            elif year_choice == "2":
                films_qs = films_qs.filter(year__lt=2015)
            elif year_choice == "3":
                films_qs = films_qs.filter(year__gte=2000, year__lte=2010)

        # dynamic multi-choice filter (M2M)
        genres = form.cleaned_data.get("genres")
        if genres:
            films_qs = films_qs.filter(genre__in=genres).distinct()

        # static multi-choice filter (decades)
        decades = form.cleaned_data.get("decade") or []
        if decades:
            decade_q = Q()
            for d in decades:
                if d == "1970s":
                    decade_q |= Q(year__gte=1970, year__lte=1979)
                elif d == "1980s":
                    decade_q |= Q(year__gte=1980, year__lte=1989)
                elif d == "1990s":
                    decade_q |= Q(year__gte=1990, year__lte=1999)
                elif d == "2000s":
                    decade_q |= Q(year__gte=2000, year__lte=2009)
                elif d == "2010s":
                    decade_q |= Q(year__gte=2010, year__lte=2019)
                elif d == "2020s":
                    decade_q |= Q(year__gte=2020, year__lte=2029)
            films_qs = films_qs.filter(decade_q)

    total_films = films_qs.count()
    latest_films = Film.objects.order_by("-id")[:5]

    return render(
        request,
        "movies/film_list.html",
        context={
            "films": films_qs,
            "forms": form,
            "total_films": total_films,
            "latest_films": latest_films,
        },
    )


@login_required(login_url="/login/")
def film_detail(request, film_id: int):
    film = get_object_or_404(
        Film.objects.select_related("category").prefetch_related("genre"),
        id=film_id,
    )

    categories = Category.objects.order_by("name")

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


@login_required(login_url="/login/")
def film_create(request):
    """Create film via external interface (GET/POST + CSRF + form validation)."""

    if request.method == "GET":
        form = CreateFilmForm()
        return render(request, "movies/film_create.html", context={"form": form})

    # POST
    form = CreateFilmForm(request.POST, request.FILES)
    if not form.is_valid():
        return render(request, "movies/film_create.html", context={"form": form})

    film = Film.objects.create(
        title=form.cleaned_data.get("title"),
        year=form.cleaned_data.get("year"),
        description=form.cleaned_data.get("description") or "",
        image=form.cleaned_data.get("image"),
        category=form.cleaned_data.get("category"),
    )

    genres = form.cleaned_data.get("genre")
    if genres:
        film.genre.set(genres)

    return redirect(f"/movies/{film.id}/")
