from django.urls import path

from .views import film_create, film_delete, film_detail, film_list

urlpatterns = [
    path("", film_list, name="film_list"),
    path("create/", film_create, name="film_create"),
    path("<int:film_id>/", film_detail, name="film_detail"),
    path("<int:film_id>/delete/", film_delete, name="film_delete"),
]
