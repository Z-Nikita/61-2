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


class SearchFilmForm(forms.Form):
    """Форма для поисковика и фильтров (GET query params).

    Реализует:
    - Поисковик (динамический)
    - Выборочная фильтрация: динамическая (категория) + статическая (по году)
    - Множественная фильтрация: динамическая (жанры M2M) + статическая (десятилетия)
    """

    YEAR_CHOICES = [
        ("", "Любой"),
        ("1", "После 2015"),
        ("2", "До 2015"),
        ("3", "2000–2010"),
    ]

    DECADE_CHOICES = [
        ("1970s", "1970–1979"),
        ("1980s", "1980–1989"),
        ("1990s", "1990–1999"),
        ("2000s", "2000–2009"),
        ("2010s", "2010–2019"),
        ("2020s", "2020–2029"),
    ]

    search = forms.CharField(
        required=False,
        label="Поиск",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Название или описание",
            }
        ),
    )

    category_id = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label="Категория (динамический фильтр)",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    year_choice = forms.ChoiceField(
        choices=YEAR_CHOICES,
        required=False,
        label="Год (статический фильтр)",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        required=False,
        label="Жанры (множественный выбор, динамический)",
        widget=forms.SelectMultiple(attrs={"class": "form-select", "size": 6}),
    )

    decade = forms.MultipleChoiceField(
        choices=DECADE_CHOICES,
        required=False,
        label="Десятилетия (множественный выбор, статический)",
        widget=forms.CheckboxSelectMultiple,
    )
