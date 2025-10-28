from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework import filters
from rest_framework import mixins

from reviews.models import Category, Genre, Titles
from .serializers import (CategorySerializer, GenreSerializer,
                          TitlesWritesSerializer, TitlesReadSerializer)


class TitlesViewSet(viewsets.ModelViewSet):
    """Вьюсет: произведения."""

    queryset = Titles.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('category__slug', 'genre__slug', 'name', 'year')

    def get_serializer_class(self):
        if self.request.method not in permissions.SAFE_METHODS:
            return TitlesWritesSerializer
        return TitlesReadSerializer

    def create(self, request, *args, **kwargs):
        write_serializer = TitlesWritesSerializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        instance = write_serializer.save()

        read_serializer = TitlesReadSerializer(instance)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        write_serializer = TitlesWritesSerializer(
            instance,
            data=request.data,
            partial=True
        )
        write_serializer.is_valid(raise_exception=True)
        instance = write_serializer.save()
        read_serializer = TitlesReadSerializer(instance)
        return Response(read_serializer.data)


class ListCreateDeleteViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'


class GenreViewSet(ListCreateDeleteViewSet):
    """Вьюсет: жанры."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(ListCreateDeleteViewSet):
    """Вьюсет: категории."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
