from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

from api.constants import MODELS_CONSTANTS
from .validators import validate_year

User = get_user_model()


class BaseModel(models.Model):
    """Абстрактная базовая модель для категорий и жанров."""

    name = models.CharField('название', max_length=MODELS_CONSTANTS['name'])
    slug = models.SlugField(
        'слаг', unique=True, max_length=MODELS_CONSTANTS['slug'])

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class BaseTextModel(models.Model):
    """Абстрактная базовая модель для отзывов и комментариев."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    text = models.TextField('Текст')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ('-pub_date',)


class Category(BaseModel):
    """Модель для представления категорий произведений."""

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Genre(BaseModel):
    """Модель для представления жанров произведений."""

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Модель для представления произведений."""

    name = models.CharField('название', max_length=MODELS_CONSTANTS['name'])
    year = models.SmallIntegerField('год', validators=[validate_year])
    description = models.TextField('описание', blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, verbose_name='категория',
        related_name='titles', blank=True, null=True
    )
    genre = models.ManyToManyField(Genre, verbose_name='Жанр')

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(BaseTextModel):
    """Модель для отзывов."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MODELS_CONSTANTS['score_min']),
            MaxValueValidator(MODELS_CONSTANTS['score_max'])
        ],
        verbose_name='Оценка'
    )

    class Meta(BaseTextModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'title'),
                name='unique_review_per_author'
            )
        ]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class Comment(BaseTextModel):
    """Модель для комментариев."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )

    class Meta(BaseTextModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
