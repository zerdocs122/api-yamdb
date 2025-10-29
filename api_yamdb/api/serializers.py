from django.db.models import Avg
from rest_framework import serializers

from reviews.models import Title, Review, Comment


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для произведений с вычисляемым рейтингом."""
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description',
            'genre', 'category', 'rating'
        )

    def get_rating(self, obj):
        """Вычисляем средний рейтинг на основе всех отзывов."""
        avg_score = obj.reviews.aggregate(Avg('score'))['score__avg']
        return round(avg_score) if avg_score is not None else None


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'title', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('title', 'author')


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев."""
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'review', 'text', 'author', 'pub_date')
        read_only_fields = ('review', 'author')
