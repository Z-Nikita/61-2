# Generated manually (compatible with Django 5.x)
from django.db import migrations


def forwards(apps, schema_editor):
    Film = apps.get_model("movies", "Film")
    Genre = apps.get_model("movies", "Genre")

    for film in Film.objects.all():
        text = (getattr(film, "genre_text", "") or "").strip()
        if not text:
            continue

        # Разделители встречаются разные: "Fantasy/Action", "Fantasy, Action" и т.п.
        parts = [
            p.strip()
            for p in text.replace("/", ",").replace(";", ",").split(",")
            if p.strip()
        ]

        for name in parts:
            genre_obj, _ = Genre.objects.get_or_create(name=name)
            film.genre.add(genre_obj)


def backwards(apps, schema_editor):
    Film = apps.get_model("movies", "Film")
    for film in Film.objects.all():
        film.genre.clear()


class Migration(migrations.Migration):
    dependencies = [
        ("movies", "0003_genre_m2m_and_image"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
