from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # AUTH & USERS
    path('me/', views.user_profile, name='user-profile'),
    path('users/', views.users_list, name='users-list'),
    
    # RESOURCES
    path('courses/', views.course_list, name='course-list'),
    path('courses/search/', views.search_courses, name='course-search'),
    path('resources/', views.resource_list, name='resource-list'),
    path('resources/upload/', views.upload_resource, name='resource-upload'),
    path('resources/<int:id>/rate/', views.rate_resource, name='resource-rate'),
    path('resources/<int:id>/ratings/', views.resource_ratings, name='resource-ratings'),
    path('resources/<int:id>/view/', views.increment_view_count, name='resource-view'),

    # CATEGORIES & TAGS
    path('categories/', views.category_list, name='category-list'),
    path('categories/<slug:slug>/', views.category_detail, name='category-detail'),
    path('tags/', views.tag_list, name='tag-list'),
    path('tags/<slug:slug>/', views.tag_threads, name='tag-threads'),

    # THREADS
    path('threads/', views.thread_list, name='thread-list'),
    path('threads/create/', views.create_thread, name='thread-create'),
    path('threads/<int:thread_id>/', views.thread_detail, name='thread-detail-api'),
    path('threads/<int:thread_id>/update/', views.update_thread, name='thread-update'),
    path('threads/<int:thread_id>/delete/', views.delete_thread, name='thread-delete'),
    path('threads/<int:thread_id>/lock/', views.lock_thread, name='thread-lock'),
    path('threads/<int:thread_id>/pin/', views.pin_thread, name='thread-pin'),
    path('threads/<int:thread_id>/like/', views.like_thread, name='thread-like'),

    # REPLIES
    path('threads/<int:thread_id>/replies/create/', views.create_reply, name='reply-create'),
    path('replies/<int:reply_id>/update/', views.update_reply, name='reply-update'),
    path('replies/<int:reply_id>/delete/', views.delete_reply, name='reply-delete'),
    path('replies/<int:reply_id>/like/', views.like_reply, name='reply-like'),
    path('replies/<int:reply_id>/mark_answer/', views.mark_answer, name='reply-mark-answer'),

    # REPORTS
    path('reports/create/', views.create_report, name='report-create'),
    path('reports/pending/', views.pending_reports, name='report-pending'),
    path('reports/<int:report_id>/resolve/', views.resolve_report, name='report-resolve'),
    path('my-reports/', views.user_reports, name='user-reports'),
]