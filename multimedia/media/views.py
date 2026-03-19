from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import generics
from .serializers import (
    UserSerializer,
    MediaSerializer,
    CommentSerializer,
    UserPublicSerializer,
    CustomTokenRefreshSerializer,
    CustomTokenObtainPairSerializer,
    LikeToggleSerializer,
    LogoutSerializer,
)
from .models import(
    Media,
    Comment,
    Like,
)
from django.contrib.auth import get_user_model
from .permissions import IsOwnerOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.exceptions import TokenError
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.parsers import JSONParser

User = get_user_model()


# Create your views here.

class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        request_body=UserSerializer,
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserUpdateView(generics.UpdateAPIView):
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]

    def get_object(self):
        return self.request.user
    

class ProfileDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"
    queryset = User.objects.all()

    def get_serializer_class(self):
        if getattr(self, 'swagger_fake_view', False):
            return UserPublicSerializer

        user_id = self.kwargs.get("id")

        try:
            if user_id and self.request.user.id == int(user_id):
                return UserSerializer
        except (TypeError, ValueError):
            pass

        return UserPublicSerializer


class MediaView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Media.objects.all()
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action == 'comment':
            return CommentSerializer
        return MediaSerializer

    def perform_create(self, serializer):
        # Assign the current logged-in user
        serializer.save(user=self.request.user)

    # Custom action for commenting
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated], parser_classes=[JSONParser])
    def comment(self, request, pk=None):
        """
        POST /media/<id>/comment/ 
        Allows logged-in user to comment on this media
        """
        media = self.get_object()  # get the Media instance
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, media=media)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny], parser_classes=[JSONParser])
    def comments(self, request, pk=None):
        """
        GET /media/<id>/comments/
        List all comments for this media
        """
        media = self.get_object()
        comments = media.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


# Simple JWT authentication for Users registration Login and Logout
# Token Obtain View
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


# Refresh View
class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer
    permission_classes = [permissions.AllowAny]


# Logout View
class LogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        # Use the serializer to validate input
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh"]

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Logout successful"},
                status=status.HTTP_200_OK
            )
        except TokenError:
            return Response(
                {"detail": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST
            )


class ToggleLikeAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Media.objects.all()  # we use this to get the media instance
    lookup_field = 'pk'
    serializer_class = LikeToggleSerializer

    def post(self, request, pk):
        # Get the media object
        media = generics.get_object_or_404(Media, pk=pk)

        # Toggle like
        like_instance, created = Like.objects.get_or_create(user=request.user, media=media)

        if not created:
            # Already liked → remove
            like_instance.delete()
            return Response({
                "liked": created,
                "like_count": media.likes.count()
            }, status=status.HTTP_200_OK)

        # Newly liked → serialize the like
        serializer = LikeToggleSerializer(like_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
