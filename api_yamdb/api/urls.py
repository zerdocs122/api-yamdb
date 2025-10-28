from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, GenreViewSet, TitlesViewSet
from .constants import API_VERSION


app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register('titles', TitlesViewSet)
router_v1.register('genres', GenreViewSet)
router_v1.register('categories', CategoryViewSet)

urlpatterns = [
    path(f'{API_VERSION}/', include(router_v1.urls)),
]
