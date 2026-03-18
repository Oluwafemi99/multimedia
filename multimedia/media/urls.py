from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserCreateView,
    UserUpdateView,
    ProfileDetailView,
    MediaView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
    ToggleLikeAPIView,
)

router = DefaultRouter()
router.register(r'media', MediaView, basename='media')

urlpatterns = [
    # User endpoints
    path('users/create/', UserCreateView.as_view(), name='user-create'),
    path('users/update/', UserUpdateView.as_view(), name='user-update'),
    path('users/<int:id>/profile/', ProfileDetailView.as_view(), name='profile-detail'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('media/<int:pk>/toggle-like/', ToggleLikeAPIView.as_view(), name='toggle-like'),

    # Media endpoints via router
    path('', include(router.urls)),
]
