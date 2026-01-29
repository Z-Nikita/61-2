from django.urls import path

from .views import film_list


urlpatterns = [
    path("", film_list, name="film_list"),
]
