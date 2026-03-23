from rest_framework import serializers
from .models import Media, Comment, Like
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import (TokenObtainPairSerializer,
                                                  TokenRefreshSerializer)
from django.contrib.auth import authenticate

User = get_user_model()


# User Serializers
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["first_name",
                  "last_name",
                  "email",
                  "age",
                  "created_at",
                  "profile_pic",
                  "password"
                  ]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('email already exists')
        return value 

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserPublicSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'profile_pic']


# media Serialiizers
class MediaSerializer(serializers.ModelSerializer):
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Media
        fields = ['user',
                  'file',
                  'title',
                  'media_type',
                  'description',
                  'created_at',
                  'like_count',
                  'comment_count',
                  ]
        read_only_fields = ['created_at',
                            'user',
                            'like_count',
                            'comment_count',
                            ]

    def validate(self, data):
        file = data.get('file')
        media_type = data.get('media_type')

        if file:
            file_name = file.name.lower()

            if media_type == 'image' and not file_name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                raise serializers.ValidationError("File must be an image")

            if media_type == 'video' and not file_name.endswith(('.mp4', '.avi', '.mov')):
                raise serializers.ValidationError("File must be a video")

            if media_type == 'audio' and not file_name.endswith(('.mp3', '.wav')):
                raise serializers.ValidationError("File must be an audio file")
            if file.size > 10*1024*1024:  # 10 MB
                raise serializers.ValidationError("File too large, max 10MB")

        return data

    def get_like_count(self, obj) -> int:
        return obj.likes.count()

    def get_comment_count(self, obj) -> int:
        return obj.comments.count()


# Comment Serializers
class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['user', 'content', 'media', 'created_at']
        read_only_fields = ['user', 'created_at', 'media']

    def validate_content(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Content cannot be empty")

        if len(value) < 4:
            raise serializers.ValidationError("Content must be at least 4 characters")

        return value


# Like Serilaizers
class LikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Like
        fields = ['user', 'media']
        read_only_fields = ['user', 'media']


class LikeToggleSerializer(serializers.ModelSerializer):
    like_count = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()

    class Meta:
        model = Like
        fields = ['id', 'user', 'media', 'liked', 'like_count']
        read_only_fields = ['id', 'user', 'media', 'liked', 'like_count']

    def get_like_count(self, obj) -> int:
        return obj.media.likes.count()

    def get_liked(self, obj) -> bool:
        return True
    

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_id'] = user.id
        token['email'] = user.email
        return token


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get('request'),
            email=email,
            password=password
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        data = super().get_token(user)

        return {
            "access": str(data.access_token),
            "refresh": str(data),
        }


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(
        required=True,
        help_text="Refresh token obtained during login"
    )
