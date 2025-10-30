import django_filters

from reviews.models import Title


class TitlesFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='category__slug')
    genre = django_filters.CharFilter(field_name='genre__slug')
    year = django_filters.NumberFilter(field_name='year')
    name = django_filters.CharFilter(field_name='name')

    class Meta:
        model = Title
        fields = ['category', 'genre', 'year', 'name']
