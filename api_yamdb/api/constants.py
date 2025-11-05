"""Константы приложения API."""
API_VERSION = 'v1'
ACCEPTABLE_HTTP_METHODS = ['get', 'post', 'patch', 'delete']
REGEXP_PATTERN = r'^[\w.@+-]+\Z'
UNACCEPTABLE_USERNAMES = ['me']
ROLE_USER: str = 'user'
ROLE_MODERATOR: str = 'moderator'
ROLE_ADMIN: str = 'admin'
ROLES = [
    (ROLE_USER, 'Аутентифицированный пользователь'),
    (ROLE_MODERATOR, 'Модератор'),
    (ROLE_ADMIN, 'Администратор'),
]
MODELS_CONSTANTS = {
    "password": 128,
    "username": 150,
    "email": 254,
    "reg_code": 50,
    'name': 256,
    'slug': 50,
    'score_min': 1,
    'score_max': 10
}
USER_NOTFOUND = {'username': 'Пользователь не найден.'}
