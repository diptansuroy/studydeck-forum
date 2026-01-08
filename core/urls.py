# COMPLETE URLS - NO DISCUSSION
# Replace entire file core/urls.py

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views


urlpatterns = [
    # ===== AUTH =====
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # ===== USER =====
    path('me/', views.user_profile, name='user-profile'),
    path('users/', views.users_list, name='users-list'),
    
    # ===== COURSES =====
    path('courses/', views.course_list, name='course-list'),
    path('search/', views.search_courses, name='search-courses'),
    
    # ===== RESOURCES =====
    path('resources/', views.resource_list, name='resource-list'),
    path('resources/upload/', views.upload_resource, name='upload-resource'),
    path('resources/<int:id>/rate/', views.rate_resource, name='rate-resource'),
    path('resources/<int:id>/ratings/', views.resource_ratings, name='resource-ratings'),
    path('resources/<int:id>/increment-view/', views.increment_view_count, name='increment-view-count'),
    
    # ===== CATEGORIES =====
    path('categories/', views.category_list, name='category-list'),
    path('categories/<slug:slug>/', views.category_detail, name='category-detail'),
    
    # ===== TAGS =====
    path('tags/', views.tag_list, name='tag-list'),
    path('tags/<slug:slug>/threads/', views.tag_threads, name='tag-threads'),
    
    # ===== THREADS =====
    path('threads/', views.thread_list, name='thread-list'),
    path('threads/create/', views.create_thread, name='create-thread'),
    path('threads/<int:thread_id>/', views.thread_detail, name='thread-detail'),
    path('threads/<int:thread_id>/update/', views.update_thread, name='update-thread'),
    path('threads/<int:thread_id>/delete/', views.delete_thread, name='delete-thread'),
    path('threads/<int:thread_id>/lock/', views.lock_thread, name='lock-thread'),
    path('threads/<int:thread_id>/pin/', views.pin_thread, name='pin-thread'),
    path('threads/<int:thread_id>/like/', views.like_thread, name='like-thread'),
    
    # ===== REPLIES =====
    path('threads/<int:thread_id>/replies/create/', views.create_reply, name='create-reply'),
    path('replies/<int:reply_id>/update/', views.update_reply, name='update-reply'),
    path('replies/<int:reply_id>/delete/', views.delete_reply, name='delete-reply'),
    path('replies/<int:reply_id>/mark-answer/', views.mark_answer, name='mark-answer'),
    path('replies/<int:reply_id>/like/', views.like_reply, name='like-reply'),
    
    # ===== REPORTS =====
    path('reports/create/', views.create_report, name='create-report'),
    path('reports/pending/', views.pending_reports, name='pending-reports'),
    path('reports/<int:report_id>/resolve/', views.resolve_report, name='resolve-report'),
    path('reports/user/', views.user_reports, name='user-reports'),
]
