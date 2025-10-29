from django.core.mail import EmailMessage


def send_confirmation_to_email(user, confirmation_code):
    """Функция отправки сообщения с кодом подтверждения.

    Принимает на вход модель пользователся и код подтверждения.
    В результате происходит сохранение сообщения от имени сервера
    в папку с кодом подтверждения для конкретного пользователя.
    """
    email = EmailMessage(
        subject='Регистрация в проекте YAMDB',
        body=(
            f'Код подтверждения для пользователя {user.username}: '
            f'{confirmation_code}'
        ),
        from_email='server YAMDB',
        to=[user.email],
        headers={'Content-Type': 'text/plain; charset=UTF-8'}
    )
    email.send()
