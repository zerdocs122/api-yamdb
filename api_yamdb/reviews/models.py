import datetime as dt

from django.db import models
from django.core.exceptions import ValidationError


class Category(models.Model):
    """Модель: категории."""

    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель: жанры."""

    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True,max_length=50)

    def __str__(self):
        return self.name


class Titles(models.Model):
    """Модель: произведения."""

    name = models.CharField(max_length=256)
    year = models.IntegerField()
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        related_name='titles', blank=True, null=True
    )
    genre = models.ManyToManyField(Genre, through='GenreTitles')

    def clean(self):
        current_year = dt.datetime.now().year
        if self.year > current_year:
            raise ValidationError({
                'year': f'Год должен быть меньше {current_year}.'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class GenreTitles(models.Model):
    """Модель: связующая между моделями произведения и жанры."""

    title_id = models.ForeignKey(Titles, on_delete=models.CASCADE)
    genre_id = models.ForeignKey(Genre, on_delete=models.CASCADE)
