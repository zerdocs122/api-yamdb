from django.urls import include, path
from rest_framework import routers

from .views import registration_view, token_get_view, UserViewSet


router_v1 = routers.DefaultRouter()
router_v1.register(r'users', UserViewSet)

urlpatterns = [
    path('v1/auth/signup/', registration_view, name='register'),
    path('v1/auth/token/', token_get_view, name='get_token'),
    path('v1/', include(router_v1.urls)),
]
