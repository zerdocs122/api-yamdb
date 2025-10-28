import datetime as dt

from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Genre, Titles, GenreTitles


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
        model = Titles
        fields = ('id', 'name', 'year', 'description', 'category', 'genre')

    def validate_year(self, value):
        if value > dt.datetime.now().year:
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего.'
            )
        return value

    def create(self, validated_data):
        genre_slugs = validated_data.pop('genre')
        title = Titles.objects.create(**validated_data)
        for genre_slug in genre_slugs:
            current_genre = Genre.objects.get(slug=genre_slug)
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

    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Titles
        fields = ['id', 'name', 'year', 'description', 'category', 'genre']
