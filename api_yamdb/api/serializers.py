import datetime as dt

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import (
    Category, Comment, Genre, GenreTitles, Review, Title
)
from api.constants import (
    MODELS_CONSTANTS, UNACCEPTABLE_USERNAMES, USER_NOTFOUND
)
from users.validators import unacceptable_name


User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'title', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('title', 'author')


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев."""
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'review', 'text', 'author', 'pub_date')
        read_only_fields = ('review', 'author')


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitlesWritesSerializer(serializers.ModelSerializer):
    """
    Сериализатор для записи объектов модели Title.

    Используется для операций создания и обновления
    произведений (POST, PATCH, DELETE).
    Обрабатывает связи с жанрами и категориями через
    список slug'ов.
    """

    genre = serializers.ListField(
        child=serializers.CharField(),
        write_only=True
    )
    description = serializers.CharField(required=False)
    category = SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'category', 'genre')

    def validate_year(self, value):
        """Валидация года выпуска произведения."""
        if value > dt.datetime.now().year:
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего.'
            )
        return value

    def validate_genre(self, value):
        """
        Валидация списка жанров произведения.

        Проверяет, что все переданные slug жанров существуют в базе данных.
        Возвращает список Genre объектов.
        """
        genres = []
        not_found_genres = []
        for genre_slug in value:
            try:
                genres.append(Genre.objects.get(slug=genre_slug))
            except Genre.DoesNotExist:
                not_found_genres.append(genre_slug)
        if not_found_genres:
            raise serializers.ValidationError(
                f'Жанры {not_found_genres} не существуют'
            )
        return genres

    def create(self, validated_data):
        """Создает новое произведение с связанными жанрами."""
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        for genre in genres:
            current_genre = genre
            GenreTitles.objects.create(genre_id=current_genre, title_id=title)
        return title

    def update(self, instance, validated_data):
        """Обновляет существующее произведение и его связи с жанрами."""
        instance.name = validated_data.get('name', instance.name)
        instance.year = validated_data.get('year', instance.year)
        instance.description = validated_data.get(
            'description', instance.description
        )
        instance.category = validated_data.get('category', instance.category)
        if 'genre' in validated_data:
            genre_slugs = validated_data.pop('genre')
            lst = []
            for genre_slug in genre_slugs:
                current_genre = Genre.objects.get(slug=genre_slug)
                lst.append(current_genre)
            instance.genre.set(lst)

        instance.save()
        return instance


class TitlesReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения объектов модели Title.

    Используется только для операций чтения (GET).
    """

    rating = serializers.SerializerMethodField()
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = [
            'id', 'name', 'year', 'description', 'category', 'genre', 'rating'
        ]

    def get_rating(self, obj):
        """Вычисляем средний рейтинг на основе всех отзывов."""
        avg_score = obj.reviews.aggregate(Avg('score'))['score__avg']
        return round(avg_score) if avg_score is not None else None


class CheckUsernameSerializer(serializers.Serializer):
    """Сериализатор для валидации поля username."""

    def validate_username(self, value):
        """Метод проверки поля username.

        Метод проверяет, что переданное значение имени пользователя
        не равно 'me'.
        """
        if value in UNACCEPTABLE_USERNAMES:
            raise serializers.ValidationError(
                'me - недопустимое имя пользователя.'
            )
        return value


class EmailConfirmationSerializer(
    CheckUsernameSerializer,
    serializers.Serializer
):
    """Сериализатор для регистрации пользователя через API."""

    email = serializers.EmailField(
        max_length=MODELS_CONSTANTS['email'],
        required=True
    )
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=MODELS_CONSTANTS['username'],
        required=True
    )

    class Meta:
        """Meta-класс сериализатора."""

        model = User
        fields = ('username', 'email')

    def validate(self, attrs):
        """Метод проверки полей username и email.

        В первую очередь проверям, есть ли пользователь с переданными данными:
        Если он есть, то возвращаем аттрибуты.
        Если нет, то проверяем, что данные не содержат повторов в базе:
        1. проверяется, существует ли в базе email, который принадлежит
        пользователю, отличному от указанного в 'username';
        2. проверяется, существует ли в базе пользователь с указанным
        'username' и принадлежит ли ему указанный 'email'.
        В случае успешного выполнения проверок снова возвращаются аттрибуты,
        значит это новый пользователь.
        """
        if User.objects.filter(
            email=attrs['email'],
            username=attrs['username']
        ).exists():
            return attrs

        if (
            User.objects.filter(email=attrs['email']).exists()
            and not User.objects.filter(
                username=attrs['username']
            ).exists()
        ):
            raise serializers.ValidationError(
                'Указанный \'email\' принадлежит другому пользователю.'
            )
        if User.objects.filter(username=attrs['username']).exists() and (
            User.objects.get(
                username=attrs['username']).email != attrs['email']
        ):
            raise serializers.ValidationError(
                'Указанный \'email\' не принадлежит этому пользователю.'
            )
        return attrs

    def create(self, validated_data):
        """Метод сохранения проверенных данных в базу данных пользователя.

        В методе проводится попытка получить пользователя по 'username',
        если пользователся еще нет в базе, то пользователь сохраняется с
        полями 'username' и 'email'.
        """
        user, _ = User.objects.get_or_create(**validated_data)
        return user


class RetriveTokenSerializer(serializers.Serializer):
    """Сериализатор для получения JWT-токена через API.

    Задаются необходимые поля для валидации получаемых данных.
    """

    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=MODELS_CONSTANTS['username'],
        required=True,
    )
    confirmation_code = serializers.CharField(
        max_length=MODELS_CONSTANTS['reg_code'],
        required=True
    )

    def validate(self, attrs):
        """Валидация пользователя и кода подтверждения.

        Очередность проверок:
        1. Проверяем, есть ли пользователь в базе. Если нет, то
        по условию задания возвращаем данные для ошибки с кодом 404.
        2. Проверяем соответвие 'confirmation_code' запрашиваемого
        пользователя в базе и присланного.
        """
        try:
            user = get_object_or_404(User, username=attrs['username'])
        except Exception:
            raise serializers.ValidationError(USER_NOTFOUND)
        if user.confirmation_code != attrs['confirmation_code']:
            raise serializers.ValidationError(
                {'confirmation_code': 'Неверный код подтверждения'}
            )
        return attrs


class UserSerializer(serializers.ModelSerializer, CheckUsernameSerializer):
    """Сериализатор модели User."""

    class Meta:
        """Meta-класс сериализатора."""

        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )

    def update(self, instance, validated_data):
        """Метод обновления данных пользователя.

        Обновляем пользовательские данные, убирая данные о роли пользователя
        при PATCH запросе на энд-поинт /users/me/.
        """
        validated_data.pop('role', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
