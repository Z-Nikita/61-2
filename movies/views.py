from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView, FormView, ListView

from users.models import Profile

from .forms import CreateFilmForm, SearchFilmForm
from .models import Category, Film


class HomeView(ListView):
    """Home page: categories with film counters."""

    model = Category
    template_name = "movies/home.html"
    context_object_name = "categories"
    paginate_by = None

    def get_queryset(self):
        return Category.objects.annotate(film_count=Count("films")).order_by("name")


class FilmListView(LoginRequiredMixin, ListView):
    """Films list with search + filters + pagination (CBV)."""

    login_url = "/login/"
    model = Film
    template_name = "movies/film_list.html"
    context_object_name = "films"
    paginate_by = 6

    def _normalized_params(self):
        """Make request.GET backward-compatible with older param names."""
        params = self.request.GET.copy()

        # older versions used `q` instead of `search`
        if params.get("q") and not params.get("search"):
            params["search"] = params.get("q")

        # older versions used `category` instead of `category_id`
        if params.get("category") and not params.get("category_id"):
            params["category_id"] = params.get("category")

        # single genre -> multi genres
        if params.get("genre") and not params.getlist("genres"):
            params.setlist("genres", [params.get("genre")])

        if params.get("genre_id") and not params.getlist("genres"):
            params.setlist("genres", [params.get("genre_id")])

        return params

    def get_queryset(self):
        # ensure profile exists for any logged-in user (e.g. superuser created via admin)
        Profile.objects.get_or_create(user=self.request.user)

        qs = (
            Film.objects.select_related("category", "profile")
            .prefetch_related("genre")
            .order_by("title")
        )

        params = self._normalized_params()
        form = SearchFilmForm(params if params else None)

        if form.is_valid():
            search = (form.cleaned_data.get("search") or "").strip()
            if search:
                qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))

            category = form.cleaned_data.get("category_id")
            if category:
                qs = qs.filter(category=category)

            # static single-choice filter
            year_choice = form.cleaned_data.get("year_choice")
            if year_choice:
                if year_choice == "1":
                    qs = qs.filter(year__gte=2015)
                elif year_choice == "2":
                    qs = qs.filter(year__lt=2015)
                elif year_choice == "3":
                    qs = qs.filter(year__gte=2000, year__lte=2010)

            # dynamic multi-choice filter (M2M)
            genres = form.cleaned_data.get("genres")
            if genres:
                qs = qs.filter(genre__in=genres).distinct()

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
                qs = qs.filter(decade_q)

        # store for context (so we don't re-normalize multiple times)
        self._params = params
        self._form = form
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # filtered form + querystring (without `page`)
        params = getattr(self, "_params", self._normalized_params())
        base_params = params.copy()
        base_params.pop("page", None)
        querystring = base_params.urlencode()

        context["forms"] = getattr(self, "_form", SearchFilmForm(params if params else None))
        context["querystring"] = querystring

        # pagination helpers for your existing template
        paginator = context.get("paginator")
        page_obj = context.get("page_obj")
        if paginator and page_obj:
            context["total_films"] = paginator.count
            context["list_pages"] = range(1, paginator.num_pages + 1)
            context["current_page"] = page_obj.number
        else:
            # fallback (no pagination)
            films = context.get("films") or []
            context["total_films"] = len(films)
            context["list_pages"] = []
            context["current_page"] = 1

        context["latest_films"] = Film.objects.order_by("-id")[:5]
        return context


class FilmDetailView(LoginRequiredMixin, DetailView):
    login_url = "/login/"
    model = Film
    template_name = "movies/film_detail.html"
    context_object_name = "film"
    pk_url_kwarg = "film_id"

    def get_queryset(self):
        return Film.objects.select_related("category", "profile").prefetch_related("genre")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        film: Film = context["film"]

        context["categories"] = Category.objects.order_by("name")

        if film.category_id:
            context["similar_films"] = (
                Film.objects.filter(category_id=film.category_id)
                .exclude(id=film.id)
                .order_by("title")[:5]
            )
        else:
            context["similar_films"] = []

        # can_delete flag for template button
        can_delete = False
        if self.request.user.is_authenticated and film.profile_id:
            profile, _ = Profile.objects.get_or_create(user=self.request.user)
            can_delete = film.profile_id == profile.id
        context["can_delete"] = can_delete

        return context


class FilmCreateView(LoginRequiredMixin, FormView):
    """Create film via external interface (GET/POST + CSRF + form validation)."""

    login_url = "/login/"
    template_name = "movies/film_create.html"
    form_class = CreateFilmForm

    def form_valid(self, form):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)

        film = Film.objects.create(
            title=form.cleaned_data.get("title"),
            year=form.cleaned_data.get("year"),
            description=form.cleaned_data.get("description") or "",
            image=form.cleaned_data.get("image"),
            category=form.cleaned_data.get("category"),
            profile=profile,
        )

        genres = form.cleaned_data.get("genre")
        if genres:
            film.genre.set(genres)

        return redirect(reverse("film_detail", kwargs={"film_id": film.id}))


class FilmDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete film (only owner)."""

    login_url = "/login/"
    model = Film
    template_name = "movies/film_confirm_delete.html"
    pk_url_kwarg = "film_id"
    success_url = reverse_lazy("film_list")

    def test_func(self):
        film: Film = self.get_object()
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        # If film has no owner, allow only superuser (optional). Otherwise only owner.
        if film.profile_id is None:
            return bool(self.request.user.is_superuser)
        return film.profile_id == profile.id

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("Недостаточно прав для удаления этого фильма")
        return super().handle_no_permission()
