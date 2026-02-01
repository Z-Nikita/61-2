from django.urls import path

from .views import film_detail, film_list

urlpatterns = [
    path("", film_list, name="film_list"),
    path("<int:film_id>/", film_detail, name="film_detail"),
]
