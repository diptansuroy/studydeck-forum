# COMPLETE VIEWS - NO DISCUSSION
# Copy entire file to core/views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
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
from .serializers import (
    CustomUserSerializer,
    CourseSerializer,
    ResourceSerializer,
    ResourceRatingSerializer,
    CategorySerializer,
    TagSerializer,
    ThreadListSerializer,
    ThreadDetailSerializer,
    ThreadCreateSerializer,
    ReplySerializer,
    LikeSerializer,
    ReportSerializer,
    ReportCreateSerializer,
    ReportUpdateSerializer,
)


# ===== PHASE 1 VIEWS (KEEP) =====

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get current user profile"""
    serializer = CustomUserSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def users_list(request):
    """List all users"""
    users = CustomUser.objects.all()
    serializer = CustomUserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def course_list(request):
    """List courses"""
    courses = Course.objects.filter(is_active=True)
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_courses(request):
    """Search courses"""
    query = request.GET.get('q', '')
    courses = Course.objects.filter(
        Q(code__icontains=query) | Q(title__icontains=query) | Q(description__icontains=query),
        is_active=True,
    )
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def resource_list(request):
    """List resources"""
    course_code = request.GET.get('course', '')
    resources = Resource.objects.all()
    if course_code:
        resources = resources.filter(course__code=course_code)
    serializer = ResourceSerializer(resources, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_resource(request):
    """Upload resource"""
    serializer = ResourceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(uploaded_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rate_resource(request, id):
    """Rate a resource"""
    resource = get_object_or_404(Resource, pk=id)
    serializer = ResourceRatingSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user, resource=resource)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def resource_ratings(request, id):
    """Get ratings for a resource"""
    resource = get_object_or_404(Resource, pk=id)
    ratings = resource.ratings.all()
    serializer = ResourceRatingSerializer(ratings, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def increment_view_count(request, id):
    """Increment resource view count"""
    resource = get_object_or_404(Resource, pk=id)
    resource.increment_view_count()
    return Response({'view_count': resource.view_count})


# ===== PHASE 3 VIEWS (NEW - NO DISCUSSION) =====

@api_view(['GET'])
@permission_classes([AllowAny])
def category_list(request):
    """List all categories"""
    categories = Category.objects.annotate(thread_count=Count('threads'))
    serializer = CategorySerializer(categories, many=True)
    return Response({
        'count': categories.count(),
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def category_detail(request, slug):
    """Get threads in a category"""
    category = get_object_or_404(Category, slug=slug)
    
    page = int(request.query_params.get('page', 1))
    page_size = 10
    start = (page - 1) * page_size
    end = start + page_size
    
    threads = category.threads.all()[start:end]
    serializer = ThreadListSerializer(threads, many=True, context={'request': request})
    
    total = category.threads.count()
    total_pages = (total + page_size - 1) // page_size
    
    return Response({
        'category': CategorySerializer(category).data,
        'count': total,
        'page': page,
        'total_pages': total_pages,
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def tag_list(request):
    """List all tags"""
    tags = Tag.objects.all()
    serializer = TagSerializer(tags, many=True)
    return Response({
        'count': tags.count(),
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def tag_threads(request, slug):
    """Get threads with a tag"""
    tag = get_object_or_404(Tag, slug=slug)
    
    page = int(request.query_params.get('page', 1))
    page_size = 10
    start = (page - 1) * page_size
    end = start + page_size
    
    threads = tag.threads.all()[start:end]
    serializer = ThreadListSerializer(threads, many=True, context={'request': request})
    
    total = tag.threads.count()
    total_pages = (total + page_size - 1) // page_size
    
    return Response({
        'tag': TagSerializer(tag).data,
        'count': total,
        'page': page,
        'total_pages': total_pages,
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def thread_list(request):
    """List all threads"""
    search_query = request.query_params.get('q', '')
    category = request.query_params.get('category', '')
    
    threads = Thread.objects.all()
    
    if search_query:
        threads = threads.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))
    
    if category:
        threads = threads.filter(category__slug=category)
    
    page = int(request.query_params.get('page', 1))
    page_size = 10
    start = (page - 1) * page_size
    end = start + page_size
    
    total = threads.count()
    threads_page = threads[start:end]
    
    serializer = ThreadListSerializer(threads_page, many=True, context={'request': request})
    total_pages = (total + page_size - 1) // page_size
    
    return Response({
        'count': total,
        'page': page,
        'total_pages': total_pages,
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def thread_detail(request, thread_id):
    """Get thread detail"""
    thread = get_object_or_404(Thread, pk=thread_id)
    serializer = ThreadDetailSerializer(thread, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_thread(request):
    """Create thread"""
    serializer = ThreadCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_thread(request, thread_id):
    """Update thread"""
    thread = get_object_or_404(Thread, pk=thread_id)
    
    if thread.author != request.user and not request.user.is_moderator():
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = ThreadCreateSerializer(thread, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(ThreadDetailSerializer(thread, context={'request': request}).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_thread(request, thread_id):
    """Delete thread"""
    thread = get_object_or_404(Thread, pk=thread_id)
    
    if thread.author != request.user and not request.user.is_moderator():
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    thread.delete()
    return Response({'message': 'Thread deleted'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def lock_thread(request, thread_id):
    """Lock thread (moderators only)"""
    thread = get_object_or_404(Thread, pk=thread_id)
    
    if not request.user.is_moderator():
        return Response({'error': 'Only moderators can lock threads'}, status=status.HTTP_403_FORBIDDEN)
    
    thread.lock_thread()
    return Response({'message': 'Thread locked'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pin_thread(request, thread_id):
    """Pin/unpin thread (moderators only)"""
    thread = get_object_or_404(Thread, pk=thread_id)
    
    if not request.user.is_moderator():
        return Response({'error': 'Only moderators can pin threads'}, status=status.HTTP_403_FORBIDDEN)
    
    thread.is_pinned = not thread.is_pinned
    thread.save()
    return Response({'message': f'Thread {"pinned" if thread.is_pinned else "unpinned"}'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_reply(request, thread_id):
    """Create reply"""
    thread = get_object_or_404(Thread, pk=thread_id)
    
    if thread.is_locked:
        return Response({'error': 'Thread is locked'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = ReplySerializer(data=request.data)
    if serializer.is_valid():
        reply = serializer.save(author=request.user, thread=thread)
        thread.increment_reply_count()
        return Response(ReplySerializer(reply, context={'request': request}).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_reply(request, reply_id):
    """Update reply"""
    reply = get_object_or_404(Reply, pk=reply_id)
    
    if reply.author != request.user and not request.user.is_moderator():
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = ReplySerializer(reply, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(ReplySerializer(reply, context={'request': request}).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_reply(request, reply_id):
    """Soft delete reply"""
    reply = get_object_or_404(Reply, pk=reply_id)
    
    if reply.author != request.user and not request.user.is_moderator():
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    reply.soft_delete()
    return Response({'message': 'Reply deleted'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_answer(request, reply_id):
    """Mark reply as answer"""
    reply = get_object_or_404(Reply, pk=reply_id)
    
    if reply.thread.author != request.user:
        return Response({'error': 'Only thread author can mark answers'}, status=status.HTTP_403_FORBIDDEN)
    
    if reply.is_answer:
        reply.is_answer = False
    else:
        reply.thread.replies.exclude(pk=reply_id).update(is_answer=False)
        reply.is_answer = True
    
    reply.save()
    return Response(ReplySerializer(reply, context={'request': request}).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_thread(request, thread_id):
    """Like/unlike thread"""
    thread = get_object_or_404(Thread, pk=thread_id)
    
    like, created = Like.objects.get_or_create(
        user=request.user,
        content_type='thread',
        thread=thread
    )
    
    if not created:
        like.delete()
        thread.like_count = max(0, thread.like_count - 1)
        action = 'unliked'
    else:
        thread.like_count += 1
        action = 'liked'
    
    thread.save(update_fields=['like_count'])
    
    return Response({
        'message': f'Thread {action}',
        'like_count': thread.like_count,
        'user_liked': created
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_reply(request, reply_id):
    """Like/unlike reply"""
    reply = get_object_or_404(Reply, pk=reply_id)
    
    like, created = Like.objects.get_or_create(
        user=request.user,
        content_type='reply',
        reply=reply
    )
    
    if not created:
        like.delete()
        reply.like_count = max(0, reply.like_count - 1)
        action = 'unliked'
    else:
        reply.like_count += 1
        action = 'liked'
    
    reply.save(update_fields=['like_count'])
    
    return Response({
        'message': f'Reply {action}',
        'like_count': reply.like_count,
        'user_liked': created
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_report(request):
    """Create report"""
    serializer = ReportCreateSerializer(data=request.data)
    if serializer.is_valid():
        report = serializer.save(reporter=request.user)
        return Response(ReportSerializer(report).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_reports(request):
    """List pending reports (moderators only)"""
    if not request.user.is_moderator():
        return Response({'error': 'Only moderators can view reports'}, status=status.HTTP_403_FORBIDDEN)
    
    reports = Report.objects.filter(status='pending').order_by('-created_at')
    
    page = int(request.query_params.get('page', 1))
    page_size = 10
    start = (page - 1) * page_size
    end = start + page_size
    
    total = reports.count()
    reports_page = reports[start:end]
    
    serializer = ReportSerializer(reports_page, many=True)
    total_pages = (total + page_size - 1) // page_size
    
    return Response({
        'count': total,
        'page': page,
        'total_pages': total_pages,
        'results': serializer.data
    })


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def resolve_report(request, report_id):
    """Resolve report (moderators only)"""
    report = get_object_or_404(Report, pk=report_id)
    
    if not request.user.is_moderator():
        return Response({'error': 'Only moderators can resolve reports'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = ReportUpdateSerializer(report, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save(moderator=request.user, resolved_at=timezone.now())
        return Response(ReportSerializer(report).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_reports(request):
    """Get reports by current user"""
    reports = Report.objects.filter(reporter=request.user)
    
    page = int(request.query_params.get('page', 1))
    page_size = 10
    start = (page - 1) * page_size
    end = start + page_size
    
    total = reports.count()
    reports_page = reports[start:end]
    
    serializer = ReportSerializer(reports_page, many=True)
    total_pages = (total + page_size - 1) // page_size
    
    return Response({
        'count': total,
        'page': page,
        'total_pages': total_pages,
        'results': serializer.data
    })
