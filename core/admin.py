# COMPLETE ADMIN - NO DISCUSSION
# Copy entire file to core/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone

from .models import (
    CustomUser,
    Course,
    Resource,
    ResourceRating,
    Category,
    Tag,
    Thread,
    Reply,
    Like,
    Report,
)


# ===== PHASE 1 ADMIN (KEEP) =====

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('bio', 'department', 'profile_picture', 'role')}),
    )
    list_display = ['email', 'first_name', 'last_name', 'department', 'role', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name', 'department']
    ordering = ['-date_joined']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'department', 'semester', 'is_active']
    list_filter = ['is_active', 'department', 'semester']
    search_fields = ['code', 'title', 'department']
    ordering = ['code']


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'resource_type', 'uploaded_by', 'view_count', 'created_at']
    list_filter = ['resource_type', 'course', 'created_at']
    search_fields = ['title', 'course__code', 'uploaded_by__email']
    readonly_fields = ['view_count', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(ResourceRating)
class ResourceRatingAdmin(admin.ModelAdmin):
    list_display = ['resource', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['resource__title', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


# ===== PHASE 3 ADMIN (NEW - NO DISCUSSION) =====

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'is_locked', 'is_pinned', 'reply_count', 'like_count', 'created_at']
    list_filter = ['category', 'is_locked', 'is_pinned', 'created_at']
    search_fields = ['title', 'author__email']
    readonly_fields = ['like_count', 'reply_count', 'created_at', 'updated_at']
    ordering = ['-is_pinned', '-created_at']


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ['thread', 'author', 'is_deleted', 'is_answer', 'like_count', 'created_at']
    list_filter = ['is_deleted', 'is_answer', 'created_at']
    search_fields = ['author__email', 'thread__title', 'content']
    readonly_fields = ['like_count', 'created_at', 'updated_at']
    ordering = ['-is_answer', '-created_at']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_type', 'thread', 'reply', 'created_at']
    list_filter = ['content_type', 'created_at']
    search_fields = ['user__email']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'reporter', 'content_type', 'status', 'moderator', 'created_at']
    list_filter = ['status', 'content_type', 'created_at']
    search_fields = ['reporter__email', 'moderator__email', 'reason']
    readonly_fields = ['reporter', 'created_at', 'resolved_at']

    actions = ['mark_resolved', 'mark_dismissed']

    def mark_resolved(self, request, queryset):
        queryset.update(status='resolved', moderator=request.user, resolved_at=timezone.now())
    mark_resolved.short_description = "Mark selected as resolved"

    def mark_dismissed(self, request, queryset):
        queryset.update(status='dismissed', moderator=request.user, resolved_at=timezone.now())
    mark_dismissed.short_description = "Mark selected as dismissed"
