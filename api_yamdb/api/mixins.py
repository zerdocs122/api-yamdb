from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import filters

from .permissions import IsAdminOrReadOnly


class ListCreateDeleteViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    """ViewSet для операций списка, создания и удаления объектов."""

    filter_backends = (filters.SearchFilter,)
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ('name',)
    lookup_field = 'slug'
