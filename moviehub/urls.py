from django.contrib import admin
from django.urls import include, path

from movies.views import home

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("movies/", include("movies.urls")),
]
