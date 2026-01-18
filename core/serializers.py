from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Course, Resource, ResourceRating, Category, Tag, Thread, Reply, Like, Report
)

User = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'bio', 'department', 'profile_picture']

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class ResourceRatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = ResourceRating
        fields = ['id', 'user', 'rating', 'review', 'created_at']

class ResourceSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField(read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    ratings = ResourceRatingSerializer(many=True, read_only=True)
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = ['id', 'course', 'course_code', 'title', 'description', 'resource_type', 'file', 'url', 'uploaded_by', 'view_count', 'created_at', 'ratings', 'avg_rating']

    def get_avg_rating(self, obj):
        ratings = obj.ratings.all()
        if ratings:
            return sum(r.rating for r in ratings) / len(ratings)
        return 0

# --- FORUM SERIALIZERS ---

class CategorySerializer(serializers.ModelSerializer):
    thread_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'thread_count']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']

class ReplySerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source='author.email', read_only=True)
    user_liked = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = ['id', 'author_email', 'content', 'created_at', 'like_count', 'is_answer', 'user_liked']

    def get_user_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

class ThreadListSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source='author.email', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    content = serializers.CharField() 
    user_liked = serializers.SerializerMethodField()
    class Meta:
        model = Thread
        fields = [
            'id', 'title', 'content', 'author_email', 'category_name', 'tags', 
            'created_at', 'like_count', 'reply_count', 'is_locked', 'is_pinned','user_liked'
        ]
    def get_user_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
class ThreadDetailSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source='author.email', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    replies = ReplySerializer(many=True, read_only=True)
    user_liked = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = [
            'id', 'title', 'content', 'author_email', 'category', 'category_name', 
            'tags', 'created_at', 'like_count', 'reply_count', 'is_locked', 
            'is_pinned', 'replies', 'user_liked'
        ]

    def get_user_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

# In core/serializers.py

class ThreadCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Tag.objects.all(), 
        required=False
    )

    class Meta:
        model = Thread
        fields = ['id', 'title', 'content', 'category', 'tags']
               
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['reason', 'content_type', 'thread', 'reply']

class ReportSerializer(serializers.ModelSerializer):
    reporter_email = serializers.EmailField(source='reporter.email', read_only=True)
    content_object = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = ['id', 'reporter_email', 'reason', 'status', 'created_at', 'content_object']

    def get_content_object(self, obj):
        if obj.thread:
            return f"Thread: {obj.thread.title}"
        if obj.reply:
            return f"Reply: {obj.reply.content[:50]}..."
        return "Unknown Content"

class ReportUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['status', 'resolution_notes']