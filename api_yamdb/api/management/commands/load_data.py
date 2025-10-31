import csv
import os
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from django.db import transaction, IntegrityError
from reviews.models import Category, Genre, Title, GenreTitles, Review, Comment
from users.models import User


class Command(BaseCommand):
    help = 'Load all CSV data from data folder into reviews models'

    BASE_DIR = 'static\data'

    # Конфигурация моделей и их CSV файлов
    MODEL_CONFIG = {
        'category': {
            'model': Category,
            'filename': 'category.csv',
            'required_fields': ['id', 'name', 'slug'],
            'fields': ['id', 'name', 'slug'],
            'model_fields': {},
            'handler': 'handle_category'
        },
        'genre': {
            'model': Genre,
            'filename': 'genre.csv',
            'required_fields': ['name', 'slug'],
            'fields': ['id', 'name', 'slug'],
            'model_fields': {},
            'handler': 'handle_genre'
        },
        'title': {
            'model': Title,
            'filename': 'titles.csv',
            'required_fields': ['name', 'year'],
            'fields': ['id', 'name', 'year', 'description'],
            'model_fields': {
                'category': {
                    'field': 'category',
                    'model': Category
                }
            },
            'handler': 'handle_titles'
        },
        'genretitles': {
            'model': GenreTitles,
            'filename': 'genre_title.csv',
            'required_fields': ['title_id', 'genre_id'],
            'fields': ['id'],
            'model_fields': {
                'title_id': {
                    'field': 'title_id',
                    'model': Title
                },
                'genre_id': {
                    'field': 'genre_id',
                    'model': Genre
                }
            },
            'handler': 'handle_genretitles'
        },
        'user': {
            'model': User,
            'filename': 'users.csv',
            'required_fields': ['username'],
            'fields': ['id', 'username', 'email', 'password', 'role' ,'confirmation_code', 'bio'],
            'model_fields': {},
            'handler': 'handle_users'
        },
        'review': {
            'model': Review,
            'filename': 'review.csv',
            'required_fields': ['title_id', 'author', 'text', 'score'],
            'fields': ['id', 'text', 'score', 'pub_date'],
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
            'handler': 'handle_review'
        },
        'comment': {
            'model': Comment,
            'filename': 'comments.csv',
            'required_fields': ['review_id', 'author', 'text'],
            'fields': ['id', 'text', 'pub_date'],
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
            'handler': 'handle_comment'
        }
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '--models',
            type=str,
            nargs='+',
            choices=list(self.MODEL_CONFIG.keys()),
            help='Specific models to load (default: all models)'
        )

    def handle(self, *args, **options):
        selected_models = options['models'] or list(self.MODEL_CONFIG.keys())

        # Определяем базовый путь к данным

        self.stdout.write(f"Loading data from: {self.BASE_DIR}")

        results = {}

        with transaction.atomic():
            for model_name in selected_models:
                config = self.MODEL_CONFIG[model_name]
                file_path = os.path.join(self.BASE_DIR, config['filename'])

                if not os.path.exists(file_path):
                    self.stdout.write(
                        self.style.WARNING(f"File not found, skipping: {file_path}")
                    )
                    continue

                try:
                    success_count = self.process_csv_file(
                        file_path, config
                    )
                    results[model_name] = success_count
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ {model_name}: {success_count} records processed"
                        )
                    )

                except Exception as e:
                    self.stderr.write(
                        self.style.ERROR(f"Error processing {model_name}: {str(e)}")
                    )
                    results[model_name] = f"Error: {str(e)}"

        # Сводка результатов
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("LOADING SUMMARY"))
        self.stdout.write("=" * 50)
        for model_name in selected_models:
            if model_name in results:
                result = results[model_name]
                status = f"✓ {result} records" if isinstance(result, int) else f"✗ {result}"
                self.stdout.write(f"{model_name:15} {status}")

    def process_csv_file(self, file_path, config):
        """Обрабатывает CSV файл для конкретной модели"""
        handler_method = getattr(self, config['handler'])

        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            # Проверка обязательных полей
            missing_fields = [
                field for field in config['required_fields']
                if field not in reader.fieldnames
            ]

            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

            success_count = 0
            for row_num, row in enumerate(reader, 1):
                try:
                    data = self.forming_data(row, config['fields'], config['model_fields'])
                    result = self.get_or_create_csv(config['model'], data)
                    # result = handler_method(row)
                    if result:
                        success_count += 1
                except Exception as e:
                    self.stderr.write(
                        f"Error in {config['filename']} line {row_num}: {str(e)}"
                    )
                    # Продолжаем обработку следующих строк
                    continue

        return success_count

    def get_or_create_csv(self,model,data):
        try:
            model.objects.get(pk=data['id'])
        except model.DoesNotExist:
            model.objects.create(**data)
            return True

    def handle_category(self, row):
        category_data = {
            'id': row.get('id',''),
            'name': row['name'],
            'slug': row['slug']
        }
        return self.get_or_create_csv(Category, category_data)

    def handle_genre(self, row):
        genre_data = {
            'id': row.get('id'),
            'name': row['name'],
            'slug': row['slug']
        }
        try:
            genre = Genre.objects.get(pk=genre_data['id'])
        except Genre.DoesNotExist:
            Genre.objects.create(**genre_data)
            return True

    def handle_titles(self, row):
        # Получаем категорию по slug
        category = Category.objects.get(pk=row['category'])
        title_data = {
            'id': row.get('id'),
            'name': row['name'],
            'year': row['year'],
            'description': row.get('description', ''),
            'category': category
        }

        return self.get_or_create_csv(Title, title_data)


    def forming_data(self, row, fields, model_fields):
        data = {}
        for  field in fields:
            data[field] = row.get(field,'')
        print(data)


        for key, value_model in model_fields.items():
            data[key] = value_model['model'].objects.get(pk=row[value_model['field']])
        print(data)
        return data

    def handle_genretitles(self, row):
        title = Title.objects.get(pk=row['title_id'])
        genre = Genre.objects.get(pk=row['genre_id'])
        # Создаем связь ManyToMany через промежуточную модель
        try:
            genre = Genre.objects.get(pk=genre_data['id'])
        except Genre.DoesNotExist:
            Genre.objects.create(**genre_data)
            return True



        genretitle, status = GenreTitles.objects.get_or_create(
            title_id=title,
            genre_id=genre
        )
        return status

    def handle_users(self, row):
        """Получает или создает пользователя"""


        users_data = {
            'id': row.get('id'),
            'username': row['username'],
            'email': row['email'],
            'role': row['role'],
            'bio': row.get('bio', ''),
            'password': row.get('password', '12345'),
            'confirmation_code': row.get('confirmation_code', '')
        }



        try:
            user = User.objects.get(pk=users_data['id'])
        except User.DoesNotExist:
            User.objects.create(**users_data)
            return True

    def handle_review(self, row):
        # Получаем произведение по названию
        title = Title.objects.get(pk=row['title_id'])
        author = User.objects.get(pk=row['author'])

        review_data = {
            'id': row.get('id'),
            'title': title,
            'author': author,
            'text': row['text'],
            'score': int(row['score'])
        }

        # Обработка даты публикации, если указана
        if 'pub_date' in row and row['pub_date']:
            review_data['pub_date'] = parse_datetime(row['pub_date'])

        try:
            review = Review.objects.get(pk=review_data['id'])
        except Review.DoesNotExist as error:
            Review.objects.create(**review_data)
            return True


    def handle_comment(self, row):
        review = Review.objects.get(pk=row['review_id'])
        author = User.objects.get(pk=row['author'])
        comment_data = {
            'id': row.get('id'),
            'review': review,
            'author': author,
            'text': row['text']
        }
        # Обработка даты публикации, если указана
        if 'pub_date' in row and row['pub_date']:
            comment_data['pub_date'] = parse_datetime(row['pub_date'])



        try:
            comment = Comment.objects.get(pk=comment_data['id'])
        except Comment.DoesNotExist:
            Comment.objects.create(**comment_data)
            return True
