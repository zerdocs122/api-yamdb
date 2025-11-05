from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import (
    Category, Comment, Genre, Review, Title
)
from api.constants import (
    MODELS_CONSTANTS, UNACCEPTABLE_USERNAMES
)
from reviews.validators import validate_year


User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'title', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('title', 'author')

    def validate_score(self, value):
        """Валидация оценки произведения."""

        if not 1 <= value <= 10:
            raise serializers.ValidationError(
                'Оценка должна быть целым числом от 1 до 10'
            )
        return value

    def validate(self, data):
        """Валидация на повторную рецензию."""

        if self.context['request'].method != 'POST':
            return data

        title = self.context['view'].title_object
        user = self.context['request'].user

        if Review.objects.filter(title=title, author=user).exists():
            raise serializers.ValidationError(
                'Вы уже оставляли отзыв на это произведение'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""
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
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""

    class Meta:
        model = Genre
        exclude = ('id',)


class TitlesWritesSerializer(serializers.ModelSerializer):
    """
    Сериализатор для операций записи POST, PUT, PATCH объектов модели Title.

    Используется для создания и обновления произведений. Принимает slug'и
    для связей с жанрами и категориями, но возвращает полные объекты в ответе.
    """

    genre = SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True
    )
    description = serializers.CharField(required=False)
    category = SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )
    year = serializers.IntegerField(validators=[validate_year])

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'category', 'genre')

    def to_representation(self, instance):
        """Преобразует внутреннее представление данных в формат для ответа."""
        return_data = super().to_representation(instance)
        return_data['category'] = CategorySerializer(instance.category).data
        return_data['genre'] = GenreSerializer(
            instance.genre.all(), many=True).data
        return return_data


class TitlesReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения объектов модели Title.

    Используется только для операций чтения GET.
    """

    rating = serializers.IntegerField(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = [
            'id', 'name', 'year', 'description', 'category', 'genre', 'rating'
        ]


class CheckUsernameSerializer(serializers.Serializer):
    """Сериализатор для валидации поля username."""

    def validate_username(self, value):
        """Метод проверки поля username.

        Метод проверяет, что переданное значение имени пользователя
        не равно 'me'.
        """
        if value in UNACCEPTABLE_USERNAMES:
            raise serializers.ValidationError(
                '{value} - недопустимое имя пользователя.'
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
        1. Пытаемся получить объект пользователя в базе, если это не удастся,
        то перехватываем ошибку User.DoesNotExist во вью-функции.
        2. Проверяем соответвие 'confirmation_code' запрашиваемого
        пользователя в базе и присланного.
        """
        user = User.objects.get(username=attrs['username'])
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
