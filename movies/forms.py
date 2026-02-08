from django import forms

from .models import Category, Genre

BAD_WORDS = ["ismar", "казино"]


class CreateFilmForm(forms.Form):
    title = forms.CharField(
        required=True,
        label="Название",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    year = forms.IntegerField(
        required=True,
        label="Год",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    description = forms.CharField(
        required=False,
        label="Описание",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}),
    )
    image = forms.ImageField(
        required=True,
        label="Изображение (постер)",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label="Категория",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    genre = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        required=False,
        label="Жанры (ManyToMany)",
        widget=forms.SelectMultiple(attrs={"class": "form-select", "size": 6}),
    )

    def clean(self):
        data = super().clean()
        title = data.get("title")
        if title in BAD_WORDS:
            raise forms.ValidationError("Это слово запрещено")

        year = data.get("year")
        if year is not None and (year < 1900 or year > 2026):
            raise forms.ValidationError("Введите корректный год")
        return data
