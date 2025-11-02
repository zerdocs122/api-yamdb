import csv
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from reviews.models import Category, Genre, Title, Review, Comment
from users.models import User


class Command(BaseCommand):
    """
    Кастомная команда Django для загрузки данных из CSV-файлов в модели.

    Поддерживает выборочную загрузку данных для конкретных
    моделей через аргументы командной строки.
    Все CSV-файлы должны находиться в директории static/data.
    """

    help = 'Загружает все данные в формате CSV из папки data в reviews models.'

    # Базовая директория для поиска CSV-файлов
    BASE_DIR = 'static/data'

    # Конфигурация моделей и их CSV файлов
    MODEL_CONFIG = {
        'category': {
            'model': Category,
            'filename': 'category.csv',
            'required_fields': ['id', 'name', 'slug'],
            'fields': ['id', 'name', 'slug'],
            'many_to_many_fields': {},
            'model_fields': {},
        },
        'genre': {
            'model': Genre,
            'filename': 'genre.csv',
            'required_fields': ['id', 'name', 'slug'],
            'fields': ['id', 'name', 'slug'],
            'many_to_many_fields': {},
            'model_fields': {},
        },
        'title': {
            'model': Title,
            'filename': 'titles.csv',
            'required_fields': ['id', 'name', 'year'],
            'fields': ['id', 'name', 'year', 'description'],
            'many_to_many_fields': {},
            'model_fields': {
                'category': {
                    'field': 'category',
                    'model': Category
                }
            },
        },
        'genretitles': {
            'model': Title,
            'filename': 'genre_title.csv',
            'required_fields': ['id', 'title_id', 'genre_id'],
            'fields': [],
            'many_to_many_fields': {
                'id': 'title_id',
                'model_id': 'genre_id',
                'many_add_field': 'genre'
            },
            'model_fields': {},
        },
        'user': {
            'model': User,
            'filename': 'users.csv',
            'required_fields': ['id', 'username', 'role'],
            'fields': ['id', 'username', 'email', 'password',
                       'role', 'confirmation_code', 'bio'],
            'many_to_many_fields': {},
            'model_fields': {},
        },
        'review': {
            'model': Review,
            'filename': 'review.csv',
            'required_fields': ['id', 'title_id', 'author', 'text', 'score'],
            'fields': ['id', 'text', 'score', 'pub_date'],
            'many_to_many_fields': {},
            'model_fields': {
                'title': {
                    'field': 'title_id',
                    'model': Title
                },
                'author': {
                    'field': 'author',
                    'model': User
                }
            },
        },
        'comment': {
            'model': Comment,
            'filename': 'comments.csv',
            'required_fields': ['id', 'review_id', 'author', 'text'],
            'fields': ['id', 'text', 'pub_date'],
            'many_to_many_fields': {},
            'model_fields': {
                'review': {
                    'field': 'review_id',
                    'model': Review
                },
                'author': {
                    'field': 'author',
                    'model': User
                }
            },
        }
    }

    def add_arguments(self, parser):
        """
        Добавляет аргументы командной строки для управления процессом загрузки.

        Args:
            parser: Парсер аргументов командной строки Django

        Добавленные аргументы:
            --models: Список моделей для выборочной загрузки
        """
        parser.add_argument(
            '--models',
            type=str,
            nargs='+',
            choices=list(self.MODEL_CONFIG.keys()),
            help='Конкретные модели для загрузки (по умолчанию: все модели)'
        )

    def handle(self, *args, **options):
        """
        Основной метод выполнения команды.

        Обрабатывает выбранные модели, загружает данные из CSV-файлов
        и выводит отчет о результатах загрузки.

        Args:
            *args: Дополнительные позиционные аргументы
            **options: Аргументы командной строки

        Процесс:
            1. Определяет модели для загрузки
            2. Обрабатывает каждую модель в транзакции
            3. Формирует сводный отчет о загрузке
        """
        selected_models = options['models'] or list(self.MODEL_CONFIG.keys())

        results = {}

        with transaction.atomic():
            for model_name in selected_models:
                config = self.MODEL_CONFIG[model_name]
                file_path = os.path.join(self.BASE_DIR, config['filename'])

                try:
                    new_records_count = self.process_csv_file(
                        file_path, config
                    )
                    results[model_name] = new_records_count
                except Exception as error:
                    results[model_name] = f'Ошибка загрузки: {str(error)}'

        self.stdout.write('\n' + 'ИТОГ ЗАГРУЗКИ')
        self.stdout.write('=' * 50)
        for model_name in selected_models:
            result = results[model_name]
            status = (f'{result} новых записей'
                      if isinstance(result, int)
                      else f'Х {result}')
            self.stdout.write(f'{model_name:15} {status}')

    def process_csv_file(self, file_path, config):
        """
        Обрабатывает CSV-файл и загружает данные в соответствующую модель.

        Args:
            file_path (str): Путь к CSV-файлу
            config (dict): Конфигурация модели из MODEL_CONFIG

        Returns:
            int: Количество успешно загруженных записей

        Процесс:
            1. Проверяет наличие обязательных полей
            2. Обрабатывает каждую строку CSV-файла
            3. Создает новые записи в базе данных
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            missing_fields = []
            for field in config['required_fields']:
                if field not in reader.fieldnames:
                    missing_fields.append(field)
            if missing_fields:
                raise ValueError(f'Отсутствуют обязательные поля: '
                                 f'{', '.join(missing_fields)}')

            success_count = 0
            for row_num, row in enumerate(reader, 1):
                try:
                    data = self.forming_data(
                        row,
                        config['fields'],
                        config['model_fields'],
                        config['many_to_many_fields']
                    )
                    result = self.get_or_create_for_csv(config['model'], data)
                    if result:
                        success_count += 1
                except Exception as e:
                    self.stderr.write(
                        f'Ошибка в {config['filename']} '
                        f'линии {row_num}: {str(e)}'
                    )
                    continue

        return success_count

    def get_or_create_for_csv(self, model, data):
        """
        Создает новую запись или добавляет связи ManyToMany
        к существующей записи.

        Для обычных моделей создает новую запись, если
        запись с таким ID не существует.
        Для связей ManyToMany добавляет связь к существующему
        объекту, если ее еще нет.

        Args:
            model: Класс модели Django
            data (dict): Данные для создания записи или добавления связи

        Returns:
            bool: True если запись была создана или связь добавлена,
            False если уже существовала
        """
        try:
            object = model.objects.get(pk=data['id'])
        except model.DoesNotExist:
            model.objects.create(**data)
            return True
        else:
            if 'many_add_field' in data:
                many_add_field = data['many_add_field']
                model_id = data['model_id']
                try:
                    getattr(object, many_add_field).get(pk=model_id)
                except Exception:
                    getattr(object, many_add_field).add(model_id)
                    return True

    def forming_data(self, row, fields, model_fields, many_to_many_fields):
        """
        Форматирует данные из CSV-строки в пригодный для модели формат.

        Args:
            row (dict): Строка данных из CSV-файла
            fields (list): Список полей для извлечения
            model_fields (dict): Конфигурация связей с другими моделями
            many_to_many_fields (dict): Конфигурация для обработки
            связей ManyToMany

        Returns:
            dict: Отформатированные данные готовые для сохранения в модель

        Процесс:
            1. Извлекает простые поля
            2. Заменяет ID связанных объектов на реальные экземпляры моделей
        """

        data = {}
        if many_to_many_fields:
            data['id'] = row.get(many_to_many_fields['id'])
            data['model_id'] = row.get(many_to_many_fields['model_id'])
            data['many_add_field'] = many_to_many_fields['many_add_field']

        for field in fields:
            data[field] = row.get(field, '')

        for key, value_model in model_fields.items():
            data[key] = (value_model['model'].objects.
                         get(pk=row[value_model['field']]))
        return data
