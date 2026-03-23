from django.contrib import admin

# Register your models here.
from .models import User, Media, Comment, Like


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "age", "created_at", "profile_pic")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("email", "first_name", "last_name")


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "media_type", "created_at")
    list_filter = ("media_type", "created_at")
    raw_id_fields = ("user",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "media", "created_at")
    raw_id_fields = ("user", "media")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("user", "media")
    raw_id_fields = ("user", "media")
