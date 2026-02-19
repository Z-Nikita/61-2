from django.urls import path

from .views import FilmCreateView, FilmDeleteView, FilmDetailView, FilmListView

urlpatterns = [
    path("", FilmListView.as_view(), name="film_list"),
    path("create/", FilmCreateView.as_view(), name="film_create"),
    path("<int:film_id>/", FilmDetailView.as_view(), name="film_detail"),
    path("<int:film_id>/delete/", FilmDeleteView.as_view(), name="film_delete"),
]
