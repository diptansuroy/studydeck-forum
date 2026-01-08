# COMPLETE SERIALIZERS - NO DISCUSSION
# Copy entire file to core/serializers.py

from rest_framework import serializers
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


# ===== PHASE 1 SERIALIZERS (KEEP) =====

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'bio', 'department', 'profile_picture', 'role', 'created_at']
        read_only_fields = ['id', 'created_at']


class CourseSerializer(serializers.ModelSerializer):
    resource_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'code', 'title', 'description', 'department', 'semester', 'credits', 'instructor', 'is_active', 'resource_count', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_resource_count(self, obj):
        return obj.resources.count()


class ResourceSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source='course.code', read_only=True)
    uploaded_by_email = serializers.CharField(source='uploaded_by.email', read_only=True)

    class Meta:
        model = Resource
        fields = ['id', 'course', 'course_code', 'title', 'description', 'resource_type', 'file', 'url', 'uploaded_by', 'uploaded_by_email', 'view_count', 'created_at']
        read_only_fields = ['id', 'uploaded_by', 'view_count', 'created_at']


class ResourceRatingSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    resource_title = serializers.CharField(source='resource.title', read_only=True)

    class Meta:
        model = ResourceRating
        fields = ['id', 'resource', 'resource_title', 'user', 'user_email', 'rating', 'review', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


# ===== PHASE 3 SERIALIZERS (NEW - NO DISCUSSION) =====

class CategorySerializer(serializers.ModelSerializer):
    thread_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'thread_count', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_thread_count(self, obj):
        return obj.threads.count()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'created_at']
        read_only_fields = ['id', 'created_at']


class ReplySerializer(serializers.ModelSerializer):
    author_email = serializers.CharField(source='author.email', read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    user_liked = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = [
            'id', 'thread', 'author', 'author_email', 'content',
            'like_count', 'user_liked', 'is_answer', 'is_deleted',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'author', 'like_count', 'is_answer', 'created_at', 'updated_at']

    def get_user_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Like.objects.filter(user=request.user, content_type='reply', reply=obj).exists()


class ThreadListSerializer(serializers.ModelSerializer):
    author_email = serializers.CharField(source='author.email', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    user_liked = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = [
            'id', 'title', 'category', 'category_name', 'author', 'author_email',
            'tags', 'like_count', 'reply_count', 'user_liked', 'is_locked',
            'is_pinned', 'created_at',
        ]
        read_only_fields = ['id', 'author', 'like_count', 'reply_count', 'is_locked', 'is_pinned', 'created_at']

    def get_user_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Like.objects.filter(user=request.user, content_type='thread', thread=obj).exists()


class ThreadDetailSerializer(serializers.ModelSerializer):
    author_email = serializers.CharField(source='author.email', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True, allow_null=True)
    tags = TagSerializer(many=True, read_only=True)
    replies = ReplySerializer(many=True, read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    user_liked = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = [
            'id', 'title', 'content', 'category', 'category_name',
            'course', 'course_code', 'author', 'author_email', 'tags',
            'replies', 'like_count', 'user_liked', 'reply_count', 'is_locked',
            'is_pinned', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'author', 'like_count', 'reply_count', 'is_locked', 'is_pinned', 'created_at', 'updated_at']

    def get_user_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Like.objects.filter(user=request.user, content_type='thread', thread=obj).exists()


class ThreadCreateSerializer(serializers.ModelSerializer):
    tag_ids = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, write_only=True, required=False)

    class Meta:
        model = Thread
        fields = ['category', 'course', 'title', 'content', 'tag_ids']

    def create(self, validated_data):
        tags = validated_data.pop('tag_ids', [])
        thread = Thread.objects.create(**validated_data)
        thread.tags.set(tags)
        return thread


class LikeSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'user', 'user_email', 'content_type', 'thread', 'reply', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class ReportSerializer(serializers.ModelSerializer):
    reporter_email = serializers.CharField(source='reporter.email', read_only=True)
    moderator_email = serializers.CharField(source='moderator.email', read_only=True, allow_null=True)
    thread_title = serializers.CharField(source='thread.title', read_only=True, allow_null=True)
    reply_preview = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            'id', 'reporter', 'reporter_email', 'moderator', 'moderator_email',
            'content_type', 'thread', 'thread_title', 'reply', 'reply_preview',
            'reason', 'status', 'resolution_notes', 'created_at', 'resolved_at',
        ]
        read_only_fields = ['id', 'moderator', 'moderator_email', 'resolution_notes', 'resolved_at', 'created_at']

    def get_reply_preview(self, obj):
        if obj.reply:
            return obj.reply.content[:100] + "..."
        return None


class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['content_type', 'thread', 'reply', 'reason']

    def validate(self, data):
        content_type = data.get('content_type')
        thread = data.get('thread')
        reply = data.get('reply')

        if content_type == 'thread' and not thread:
            raise serializers.ValidationError("Thread required for thread report")
        if content_type == 'reply' and not reply:
            raise serializers.ValidationError("Reply required for reply report")
        return data


class ReportUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['status', 'resolution_notes']
