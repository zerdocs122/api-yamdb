from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TitleViewSet, ReviewViewSet, CommentViewSet

v1_router = DefaultRouter()

v1_router.register(
    r'titles', TitleViewSet, basename='titles'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/', include(v1_router.urls)),
from .views import CategoryViewSet, GenreViewSet, TitlesViewSet
from .constants import API_VERSION


app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register('titles', TitlesViewSet)
router_v1.register('genres', GenreViewSet)
router_v1.register('categories', CategoryViewSet)

urlpatterns = [
    path(f'{API_VERSION}/', include(router_v1.urls)),
from rest_framework import routers

from .views import registration_view, token_get_view, UserViewSet


router_v1 = routers.DefaultRouter()
router_v1.register(r'users', UserViewSet)

urlpatterns = [
    path('v1/auth/signup/', registration_view, name='register'),
    path('v1/auth/token/', token_get_view, name='get_token'),
    path('v1/', include(router_v1.urls)),
]
