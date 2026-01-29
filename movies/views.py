from django.shortcuts import render

from .models import Film


def film_list(request):
    films = Film.objects.all().order_by("title")
    return render(request, "film_list.html", context={"films": films})
