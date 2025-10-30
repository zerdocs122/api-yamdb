import datetime as dt

from django.contrib.auth import get_user_model
from django.db.models import Avg
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import (
    Category, Comment, Genre, GenreTitles, Review, Title
)


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
    """Сериализатор: категории."""

    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор: жанры."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitlesWritesSerializer(serializers.ModelSerializer):
    """
    Сериализатор: произведения, используется для
    методов POST, PUT, PATCH, DELETE.
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
        if value > dt.datetime.now().year:
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего.'
            )
        return value

    def validate_genre(self, value):
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
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        for genre in genres:
            current_genre = genre
            GenreTitles.objects.create(genre_id=current_genre, title_id=title)
        return title

    def update(self, instance, validated_data):
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
    """Сериализатор: произведения, используется для метода GET."""

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
        if value == 'me':
            raise serializers.ValidationError(
                'me - недопустимое имя пользователя.'
            )
        return value


class EmailConfirmationSerializer(
    CheckUsernameSerializer,
    serializers.Serializer
):
    """Сериализатор для регистрации пользователя через API."""

    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=150,
        required=True
    )

    class Meta:
        """Meta-класс сериализатора."""

        model = User
        fields = ('username', 'email')

    def validate(self, attrs):
        """Метод проверки полей username и email.

        В методе проверяется, что:
        - в запросе существуют обязательные ключи 'username' и 'email';
        - проверяется, существует ли в базе email, который принадлежит
        пользователю, отличному от указанного в 'username';
        - проверяется, существует ли в базе пользователь с указанным 'username'
        и принадлежит ли ему указанный 'email'.
        В случае выполнения проверок возвращаются необходимые данные.
        """
        if attrs.get('email') and attrs.get('username'):
            if (
                User.objects.filter(email=attrs['email']).exists()
                and not User.objects.filter(
                    username=attrs['username']
                ).exists()
            ):
                raise serializers.ValidationError(
                    'Поля \'username\' и \'email\' должны быть уникальны.'
                )
            if User.objects.filter(username=attrs['username']).exists() and (
                User.objects.get(
                    username=attrs['username']).email != attrs['email']
            ):
                raise serializers.ValidationError(
                    'Указанный \'email\' не принадлежит существующему '
                    'пользователю.'
                )
        return attrs

    def create(self, validated_data):
        """Метод сохранения проверенных данных в базу данных пользователя.

        В методе проводится попытка получить пользователя по 'username',
        если пользователся еще нет в базе, то пользователь сохраняется с
        полями 'username' и 'email'.
        """
        try:
            user = User.objects.get(username=validated_data['username'])
        except User.DoesNotExist:
            user = User.objects.create_user(**validated_data)
        return user


class RetriveTokenSerializer(serializers.Serializer):
    """Сериализатор для получения JWT-токена через API.

    Задаются необходимые поля для валидации получаемых данных.
    """

    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=150,
        required=True
    )
    confirmation_code = serializers.CharField(max_length=50, required=True)


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
