from django.contrib import admin

from .models import Category, Genre, Title, Comment, Review


admin.site.empty_value_display = 'Не задано'


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'description',
        'year',
        'category',
        'get_genre'
    )
    list_editable = (
        'category',
    )
    autocomplete_fields = ('genre',)
    search_fields = ('name',)
    list_filter = ('category', 'genre')
    list_display_links = ('name',)

    def get_genre(self, instance):
        return [genre.name for genre in instance.genre.all()]

    get_genre.short_description = 'Жанр'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name',)
    list_display_links = ('name',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name',)
    list_display_links = ('name',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'score',
        'pub_date',
    )
    search_fields = ('title__name',)
    list_display_links = ('title',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'review',
        'author',
        'pub_date',
    )
    search_fields = ('review__title__name',)
    list_display_links = ('review',)
