from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from movies.views import home
from users.views import login_user, logout_user, profile, register, update_profile

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("profile/", profile, name="profile"),
    path("profile/update/", update_profile, name="update_profile"),
    path("movies/", include("movies.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
