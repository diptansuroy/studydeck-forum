
from .utils import notify_mentions, notify_thread_reply, notify_thread_status # <--- ADD THIS
from rest_framework.decorators import api_view, permission_classes, authentication_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication, BasicAuthentication


# Postgres Specific Search
from django.contrib.postgres.search import TrigramSimilarity

from .models import (
    CustomUser, Course, Resource, ResourceRating,
    Category, Tag, Thread, Reply, Like, Report
)
from .serializers import (
    CustomUserSerializer, CourseSerializer, ResourceSerializer, ResourceRatingSerializer,
    CategorySerializer, TagSerializer, ThreadListSerializer, ThreadDetailSerializer,
    ThreadCreateSerializer, ReplySerializer, LikeSerializer, ReportSerializer,
    ReportCreateSerializer, ReportUpdateSerializer
)
class BurstRateThrottle(UserRateThrottle):
    scope = 'burst'


@api_view(['GET'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def user_profile(request):
    serializer = CustomUserSerializer(request.user)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def users_list(request):
    users = CustomUser.objects.all()
    serializer = CustomUserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def course_list(request):
    courses = Course.objects.filter(is_active=True)
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def search_courses(request):
    query = request.GET.get('q', '')
    courses = Course.objects.filter(
        Q(code__icontains=query) | Q(title__icontains=query),
        is_active=True,
    )
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def resource_list(request):
    course_code = request.GET.get('course', '')
    resources = Resource.objects.all()
    if course_code:
        resources = resources.filter(course__code=course_code)
    serializer = ResourceSerializer(resources, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def upload_resource(request):
    serializer = ResourceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(uploaded_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def rate_resource(request, id):
    resource = get_object_or_404(Resource, pk=id)
    serializer = ResourceRatingSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user, resource=resource)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def resource_ratings(request, id):
    resource = get_object_or_404(Resource, pk=id)
    ratings = resource.ratings.all()
    serializer = ResourceRatingSerializer(ratings, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def increment_view_count(request, id):
    resource = get_object_or_404(Resource, pk=id)
    resource.increment_view_count()
    return Response({'view_count': resource.view_count})

@api_view(['GET'])
@permission_classes([AllowAny])
def category_list(request):
    categories = Category.objects.annotate(thread_count=Count('threads'))
    serializer = CategorySerializer(categories, many=True)
    return Response({'count': categories.count(), 'results': serializer.data})

@api_view(['GET'])
@permission_classes([AllowAny])
def category_detail(request, slug):
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
        'count': total, 'page': page, 'total_pages': total_pages,
        'results': serializer.data
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def tag_list(request):
    tags = Tag.objects.all()
    serializer = TagSerializer(tags, many=True)
    return Response({'count': tags.count(), 'results': serializer.data})

@api_view(['GET'])
@permission_classes([AllowAny])
def tag_threads(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    threads = tag.threads.all()
    serializer = ThreadListSerializer(threads, many=True, context={'request': request})
    return Response({'tag': TagSerializer(tag).data, 'results': serializer.data})

@api_view(['GET'])
@permission_classes([AllowAny])
def thread_list(request):
    """List threads with Fuzzy Search & Sorting"""
    search_query = request.query_params.get('q', '')
    category = request.query_params.get('category', '')
    tag_slug = request.query_params.get('tag', '')
    sort_by = request.query_params.get('sort', 'latest') # 'latest' or 'popular'
    
    threads = Thread.objects.all()
    
    if search_query:
        try:
            threads = threads.annotate(
                similarity=TrigramSimilarity('title', search_query) + TrigramSimilarity('content', search_query)
            ).filter(similarity__gt=0.1).order_by('-similarity')
        except Exception:
            threads = threads.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))
    
    if category:
        threads = threads.filter(category__slug=category)
    if tag_slug:
        threads = threads.filter(tags__slug=tag_slug)
        
    # 2. Sorting Logic
    if sort_by == 'popular':
        threads = threads.order_by('-like_count', '-created_at')
    else:
        threads = threads.order_by('-created_at')

    # Pagination
    page = int(request.query_params.get('page', 1))
    page_size = 10
    start = (page - 1) * page_size
    end = start + page_size
    total = threads.count()
    threads_page = threads[start:end]
    
    serializer = ThreadListSerializer(threads_page, many=True, context={'request': request})
    total_pages = (total + page_size - 1) // page_size
    
    return Response({
        'count': total, 'page': page, 'total_pages': total_pages,
        'results': serializer.data
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def thread_detail(request, thread_id):
    thread = get_object_or_404(Thread, pk=thread_id)
    serializer = ThreadDetailSerializer(thread, context={'request': request})
    return Response(serializer.data)

@api_view(['POST'])
@authentication_classes([JWTAuthentication, SessionAuthentication]) # <--- ADDED SessionAuthentication
@permission_classes([IsAuthenticated])
@throttle_classes([BurstRateThrottle])
def create_thread(request):
    """Create thread + Check Mentions"""
    # ... keep your existing logic ...
    serializer = ThreadCreateSerializer(data=request.data)
    if serializer.is_valid():
        thread = serializer.save(author=request.user)
        notify_mentions(thread.content, request.user, thread, f"/thread/{thread.id}/")
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
@throttle_classes([BurstRateThrottle])
def create_reply(request, thread_id):
    """Create reply + Notify Author + Check Mentions"""
    try:
        thread = get_object_or_404(Thread, pk=thread_id)
        if thread.is_locked:
            return Response({'error': 'Thread is locked'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ReplySerializer(data=request.data)
        if serializer.is_valid():
            reply = serializer.save(author=request.user, thread=thread)
            
            # Update count
            thread.reply_count += 1
            thread.save(update_fields=['reply_count'])
            
            # --- NOTIFICATION LOGIC ---
            # 1. Notify Thread Author
            notify_thread_reply(thread, request.user, reply.content)
            
            # 2. Notify anyone mentioned in the reply (@username)
            notify_mentions(reply.content, request.user, thread, f"/thread/{thread.id}/")
            # --------------------------

            return Response(ReplySerializer(reply, context={'request': request}).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def lock_thread(request, thread_id):
    """Lock + Notify"""
    thread = get_object_or_404(Thread, pk=thread_id)
    if not request.user.is_moderator():
        return Response({'error': 'Only moderators can lock threads'}, status=status.HTTP_403_FORBIDDEN)
    
    thread.lock_thread()
    # Notify Author
    notify_thread_status(thread, "LOCKED", request.user)
    
    return Response({'message': 'Thread locked'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def pin_thread(request, thread_id):
    """Pin + Notify"""
    thread = get_object_or_404(Thread, pk=thread_id)
    if not request.user.is_moderator():
        return Response({'error': 'Only moderators can pin threads'}, status=status.HTTP_403_FORBIDDEN)
    
    thread.is_pinned = not thread.is_pinned
    thread.save()
    
    # Notify Author
    action = "PINNED" if thread.is_pinned else "UNPINNED"
    notify_thread_status(thread, action, request.user)

    return Response({'message': f'Thread {action.lower()}'}, status=status.HTTP_200_OK)

@api_view(['PATCH'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_thread(request, thread_id):
    thread = get_object_or_404(Thread, pk=thread_id)
    if thread.author != request.user and not request.user.is_moderator():
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    serializer = ThreadCreateSerializer(thread, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(ThreadDetailSerializer(thread, context={'request': request}).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_thread(request, thread_id):
    thread = get_object_or_404(Thread, pk=thread_id)
    if thread.author != request.user and not request.user.is_moderator():
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    thread.delete()
    return Response({'message': 'Thread deleted'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['PATCH'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_reply(request, reply_id):
    reply = get_object_or_404(Reply, pk=reply_id)
    if reply.author != request.user and not request.user.is_moderator():
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    serializer = ReplySerializer(reply, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(ReplySerializer(reply, context={'request': request}).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_reply(request, reply_id):
    reply = get_object_or_404(Reply, pk=reply_id)
    if reply.author != request.user and not request.user.is_moderator():
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    thread = reply.thread
    reply.delete()
    thread.reply_count = max(0, thread.reply_count - 1)
    thread.save(update_fields=['reply_count'])
    return Response({'message': 'Reply permanently deleted'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def mark_answer(request, reply_id):
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
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def like_thread(request, thread_id):
    thread = get_object_or_404(Thread, pk=thread_id)
    like, created = Like.objects.get_or_create(user=request.user, content_type='thread', thread=thread)
    if not created:
        like.delete()
        thread.like_count = max(0, thread.like_count - 1)
        action = 'unliked'
    else:
        thread.like_count += 1
        action = 'liked'
    thread.save(update_fields=['like_count'])
    return Response({'message': f'Thread {action}', 'like_count': thread.like_count, 'user_liked': created})

@api_view(['POST'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def like_reply(request, reply_id):
    reply = get_object_or_404(Reply, pk=reply_id)
    like, created = Like.objects.get_or_create(user=request.user, content_type='reply', reply=reply)
    if not created:
        like.delete()
        reply.like_count = max(0, reply.like_count - 1)
        action = 'unliked'
    else:
        reply.like_count += 1
        action = 'liked'
    reply.save(update_fields=['like_count'])
    return Response({'message': f'Reply {action}', 'like_count': reply.like_count, 'user_liked': created})

@api_view(['POST'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
@throttle_classes([BurstRateThrottle]) # <--- RATE LIMITING APPLIED
def create_report(request):
    serializer = ReportCreateSerializer(data=request.data)
    if serializer.is_valid():
        report = serializer.save(reporter=request.user)
        return Response(ReportSerializer(report).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def pending_reports(request):
    if not request.user.is_moderator():
        return Response({'error': 'Only moderators can view reports'}, status=status.HTTP_403_FORBIDDEN)
    reports = Report.objects.filter(status='pending').order_by('-created_at')
    # ... (pagination simplified)
    serializer = ReportSerializer(reports, many=True)
    return Response({'count': reports.count(), 'results': serializer.data})

@api_view(['PATCH'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def resolve_report(request, report_id):
    report = get_object_or_404(Report, pk=report_id)
    if not request.user.is_moderator():
        return Response({'error': 'Only moderators can resolve reports'}, status=status.HTTP_403_FORBIDDEN)
    serializer = ReportUpdateSerializer(report, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save(moderator=request.user, resolved_at=timezone.now())
        return Response(ReportSerializer(report).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def user_reports(request):
    reports = Report.objects.filter(reporter=request.user)
    serializer = ReportSerializer(reports, many=True)
    return Response({'count': reports.count(), 'results': serializer.data})