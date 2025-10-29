from http import HTTPStatus
import secrets

from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

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
    """Функция для регистрации и отправки кода подтверждения.

    Функция осуществляет регистрацию пользователя, если он ранее
    не был зарегистрирован. Принимает на вход словарь в POST-запросе
    с обязательными ключами: 'username' и 'email'.
    Так же в результате запроса на указанную электронную почту
    высылается код подтверждения для получения JWT-токена доступа.
    Получить код можно неограниченное число раз.
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
    """ViewSet для работы с пользователями по API."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
