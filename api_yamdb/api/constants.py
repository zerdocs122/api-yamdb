from api.utils import get_role_length

API_VERSION = 'v1'
ACCEPTABLE_HTTP_METHODS = ['get', 'post', 'patch', 'delete']
UNACCEPTABLE_USERNAMES = ['me']
ROLES = [
        ('user', 'Аутентифицированный пользователь'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор'),
    ]
MODELS_CONSTANTS = {
    "password": 128,
    "username": 150,
    "email": 254,
    "role": get_role_length(ROLES),
    "reg_code": 50
}
USER_NOTFOUND = {'username': 'Пользователь не найден.'}
