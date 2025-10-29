from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions

from reviews.models import Title, Review
from .serializers import TitleSerializer, ReviewSerializer, CommentSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для произведений."""
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для отзывов."""
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @property
    def title_object(self):
        "Возвращает объект произведения для текущего запроса."
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Отзывы только к конкретному произведению."""
        return self.title_object.reviews.all()

    def perform_create(self, serializer):
        """Привязываем автора и произведение автоматически."""
        serializer.save(author=self.request.user, title=self.title_object)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для комментариев."""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @property
    def review_object(self):
        """Возвращает объект отзыва для текущего запроса."""
        return get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
            )

    def get_queryset(self):
        """Комментарии к конкретному отзыву."""
        return self.review_object.comment.all()

    def perform_create(self, serializer):
        """Привязываем автора и отзыв автоматически."""
        serializer.save(author=self.request.user, review=self.review_object)
