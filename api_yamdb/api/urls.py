from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .constants import API_VERSION
from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    registration_view,
    ReviewViewSet,
    TitlesViewSet,
    token_get_view,
    UserViewSet
)


router_v1 = DefaultRouter()
router_v1.register(r'users', UserViewSet)
router_v1.register('titles', TitlesViewSet)
router_v1.register('genres', GenreViewSet)
router_v1.register('categories', CategoryViewSet)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)


urlpatterns = [
    path(f'{API_VERSION}/auth/signup/', registration_view, name='register'),
    path(f'{API_VERSION}/auth/token/', token_get_view, name='get_token'),
    path(f'{API_VERSION}/', include(router_v1.urls)),
]
