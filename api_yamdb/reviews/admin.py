from django.contrib import admin

from .models import Category, Genre, Title


admin.site.empty_value_display = 'Не задано'


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


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name',)
    list_display_links = ('name',)


class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name',)
    list_display_links = ('name',)


admin.site.register(Title, TitleAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)