from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .forms import LoginForms, RegisterForms

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
        User.objects.create_user(
            username=forms.cleaned_data.get("username"),  # pyright: ignore[reportArgumentType]
            password=forms.cleaned_data.get("password"),
        )
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
    return redirect("/movies/")


def logout_user(request):
    logout(request)
    return redirect("/")
