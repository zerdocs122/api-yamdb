from django.contrib import admin

from .models import Category, Genre, Title


admin.site.empty_value_display = 'Не задано'


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'description',
        'year',
        'category',
    )
    list_editable = (
        'category',
    )
    search_fields = ('name',)
    list_filter = ('category', 'genre')
    list_display_links = ('name',)


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
