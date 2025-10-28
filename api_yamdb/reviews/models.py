from django.db import models


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

    def __str__(self):
        return self.name


class GenreTitles(models.Model):
    """Модель: связующая между моделями произведения и жанры."""

    title_id = models.ForeignKey(Titles, on_delete=models.CASCADE)
    genre_id = models.ForeignKey(Genre, on_delete=models.CASCADE)
