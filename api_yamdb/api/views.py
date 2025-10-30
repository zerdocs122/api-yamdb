from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework import filters

from reviews.models import Category, Genre, Titles
from .serializers import (CategorySerializer, GenreSerializer,
                          TitlesWritesSerializer, TitlesReadSerializer)
from .mixins import ListCreateDeleteViewSet


class TitlesViewSet(viewsets.ModelViewSet):
    """Вьюсет: произведения."""

    queryset = Titles.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('category__slug', 'genre__slug', 'name', 'year')

    def get_serializer_class(self):
        if self.request.method not in permissions.SAFE_METHODS:
            return TitlesWritesSerializer
        return TitlesReadSerializer

    def create(self, request, *args, **kwargs):
        write_serializer = TitlesWritesSerializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        instance = write_serializer.save()

        read_serializer = TitlesReadSerializer(instance)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        write_serializer = TitlesWritesSerializer(
            instance,
            data=request.data,
            partial=True
        )
        write_serializer.is_valid(raise_exception=True)
        instance = write_serializer.save()
        read_serializer = TitlesReadSerializer(instance)
        return Response(read_serializer.data)


class GenreViewSet(ListCreateDeleteViewSet):
    """Вьюсет: жанры."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(ListCreateDeleteViewSet):
    """Вьюсет: категории."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
from http import HTTPStatus
import secrets

from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .permissions import IsAdmin
from .serializers import EmailConfirmationSerializer, RetriveTokenSerializer
from .utils import send_confirmation_to_email as send_email


from users.models import User
from api.serializers import UserSerializer


User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def registration_view(request):
    """Функция для регистрации и отправки кода подтверждения.

    Функция осуществляет регистрацию пользователя, если он ранее
    не был зарегистрирован. Принимает на вход словарь в POST-запросе
    с обязательными ключами: 'username' и 'email'.
    Так же в результате запроса на указанную электронную почту
    высылается код подтверждения для получения JWT-токена доступа.
    Получить код можно неограниченное число раз.
    """
    serializer = EmailConfirmationSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
    except Exception:
        return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)

    user = serializer.save()
    generated_code = secrets.token_urlsafe(32)
    User.objects.filter(username=user.username).update(
        confirmation_code=generated_code
    )
    send_email(user, generated_code)

    return Response(request.data, status=HTTPStatus.OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def token_get_view(request):
    """Функция получения JWT-токена по запросу.

    Принимает на вход обязательные поля 'username' и 'confirmation_code'.
    Проверяет наличие в базе юзера, который запрашивает токен, проверяет
    соответвие 'confirmation_code' в базе и присланного.
    В результате выдает JWT-токен доступа.
    """
    serializer = RetriveTokenSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
    except Exception:
        return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)
    username = serializer.validated_data.get('username')
    confirmation_code = serializer.validated_data.get('confirmation_code')
    user = get_object_or_404(User, username=username)

    if confirmation_code == user.confirmation_code:
        token = RefreshToken.for_user(user)

        return Response(
            {'token': f'{token.access_token}'},
            status=HTTPStatus.OK
        )

    return Response(
        {'confirmation_code': 'Неверный код подтверждения'},
        status=HTTPStatus.BAD_REQUEST,
    )


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с пользователями по эндпоинту /users/.

    Вьюсет отдает список пользователей администратору при GET запросе и
    позволяет создать пользователя при POST запросе.

    Через этот вьюсет администратор может получать информацию о конкретном
    пользователе через GET-запрос, обновлять информацию о пользователе через
    PATCH-запрос, удалять пользователя через DELETE-запрос.

    Отдельно для эндпоинта /users/me/ доступна возможность зарегистрирвоанному
    пользователю увидеть свои данные через GET-запрос и обновить данные через
    PATCH-запрос.
    """

    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        ['GET', 'PATCH'],
        permission_classes=(IsAuthenticated,),
        detail=False,
        url_path='me',
    )
    def me_view_function(self, request):
        """Функция обработки запросов через эндпоинт /users/me/."""
        if request.method == 'GET':
            serializer = self.serializer_class(request.user)
            return Response(serializer.data, status=HTTPStatus.OK)
        serializer = self.serializer_class(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.update(request.user, serializer.validated_data)
        return Response(serializer.data, status=HTTPStatus.OK)
