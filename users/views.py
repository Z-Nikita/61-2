from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .forms import LoginForms, RegisterForms, UpdateProfileForm
from .models import Profile

# Create your views here.

# Аунтентификация - поиск пользователя в бд
# Авторизация - проверка прав доступа пользователя
# Регистрация - создание нового пользователя


def register(request):
    if request.method == "GET":
        forms = RegisterForms()
        return render(request, "users/register.html", context={"forms": forms})

    if request.method == "POST":
        forms = RegisterForms(request.POST)
        if not forms.is_valid():
            return render(
                request,
                "users/register.html",
                context={"forms": forms},
            )

        user = User.objects.create_user(
            username=forms.cleaned_data.get("username"),  # pyright: ignore[reportArgumentType]
            password=forms.cleaned_data.get("password"),
        )
        Profile.objects.get_or_create(user=user)

    return redirect("/movies/")


def login_user(request):
    if request.method == "GET":
        forms = LoginForms()
        return render(request, "users/login.html", context={"forms": forms})

    if request.method == "POST":
        forms = LoginForms(request.POST)
        if not forms.is_valid():
            return render(
                request,
                "users/login.html",
                context={"forms": forms},
            )

        user = authenticate(
            request,
            username=forms.cleaned_data.get("username"),
            password=forms.cleaned_data.get("password"),
        )

        if user is None:
            # неверный логин/пароль
            return render(
                request,
                "users/login.html",
                context={"forms": forms, "error": "Неверный логин или пароль"},
            )

        login(request, user)
        Profile.objects.get_or_create(user=user)

    return redirect("/movies/")


def logout_user(request):
    logout(request)
    return redirect("/")


@login_required(login_url="/login/")
def profile(request):
    Profile.objects.get_or_create(user=request.user)

    # фильмы пользователя (по полю profile у Film)
    from movies.models import Film  # local import to avoid circular import in startup

    my_films = Film.objects.filter(profile=request.user.profile).order_by("-id")

    return render(
        request,
        "users/profile.html",
        context={
            "my_films": my_films,
        },
    )


@login_required(login_url="/login/")
def update_profile(request):
    prof, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "GET":
        forms = UpdateProfileForm(
            initial={
                "username": request.user.username,
                "email": request.user.email,
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "age": prof.age,
            }
        )
        return render(request, "users/update_profile.html", context={"forms": forms})

    # POST
    forms = UpdateProfileForm(request.POST, request.FILES)
    if not forms.is_valid():
        return render(request, "users/update_profile.html", context={"forms": forms})

    # user fields
    new_username = forms.cleaned_data.get("username")
    if new_username and User.objects.filter(username=new_username).exclude(pk=request.user.pk).exists():
        forms.add_error("username", "Этот логин уже занят")
        return render(request, "users/update_profile.html", context={"forms": forms})

    request.user.username = new_username

    request.user.email = forms.cleaned_data.get("email") or ""
    request.user.first_name = forms.cleaned_data.get("first_name") or ""
    request.user.last_name = forms.cleaned_data.get("last_name") or ""
    request.user.save()

    # profile fields
    prof.age = forms.cleaned_data.get("age")
    new_image = forms.cleaned_data.get("image")
    if new_image:
        prof.image = new_image
    prof.save()

    return redirect("/profile/")
