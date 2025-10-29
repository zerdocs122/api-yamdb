from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class EmailConfirmationSerializer(serializers.Serializer):
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


class UserSerializer(serializers.ModelSerializer):
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

    def update(self, instance, validated_data):
        """Метод обновления данных пользователя.

        Обновляем пользовательские данные, убирая данные о роли пользователя
        при PATCH запросе на энд-поинт /users/me/, если пользователь
        не является администратором.
        """
        validated_data.pop('role', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
