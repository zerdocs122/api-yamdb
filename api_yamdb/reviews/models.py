import datetime as dt

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


User = get_user_model()


class Category(models.Model):
    """Модель для представления категорий произведений."""

    name = models.CharField('название', max_length=256)
    slug = models.SlugField('слаг', unique=True, max_length=50)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель для представления жанров произведений."""

    name = models.CharField('название', max_length=256)
    slug = models.SlugField('слаг', unique=True, max_length=50)

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель для представления произведений."""

    name = models.CharField('название', max_length=256)
    year = models.IntegerField('год')
    description = models.TextField('описание', blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, verbose_name='категория',
        related_name='titles', blank=True, null=True
    )
    genre = models.ManyToManyField(
        Genre, through='GenreTitles', verbose_name='жанр'
    )

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'

    def clean(self):
        """Проверяет валидность года выпуска произведения."""
        current_year = dt.datetime.now().year
        if self.year > current_year:
            raise ValidationError({
                'year': f'Год должен быть меньше {current_year}.'
            })

    def save(self, *args, **kwargs):
        """Сохраняет объект с предварительной полной валидацией."""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class GenreTitles(models.Model):
    """Модель: связующая между моделями произведения и жанры."""

    title_id = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre_id = models.ForeignKey(Genre, on_delete=models.CASCADE)


class Review(models.Model):

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews')

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    text = models.TextField()
    score = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:

        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'title'),
                name='unique_review_per_author'
            )
        ]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class Comment(models.Model):

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:

        ordering = ('pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
