from django.contrib import admin

# Register your models here.
from .models import User, Media, Comment, Like


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "first_name", "last_name", "age", "is_staff", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "media_type", "created_at")
    list_filter = ("media_type", "created_at")
    search_fields = ("title", "description", "user__username")
    raw_id_fields = ("user",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "media", "created_at")
    search_fields = ("content", "user__username", "media__title")
    raw_id_fields = ("user", "media")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("user", "media")
    search_fields = ("user__username", "media__title")
    raw_id_fields = ("user", "media")
