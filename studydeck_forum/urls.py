from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),      # Connects the API URLs above
    path('accounts/', include('allauth.urls')), # Connects Google Login

    # --- FRONTEND PAGES ---
    # Login & Home
    path('login/', TemplateView.as_view(template_name='forum/login.html'), name='login'),
    path('forum/', TemplateView.as_view(template_name='forum/index.html'), name='forum'),
    path('', TemplateView.as_view(template_name='forum/index.html'), name='home'),
    
    # Thread Pages
    path('forum/create/', TemplateView.as_view(template_name='forum/create_thread.html'), name='thread-create-page'),
    path('thread/<int:pk>/', TemplateView.as_view(template_name='forum/thread_detail.html'), name='thread-detail'), # <--- CRITICAL
    
    # Moderator Dashboard
    path('moderator/', TemplateView.as_view(template_name='forum/moderator.html'), name='moderator-dashboard'),
]

# Media/Static files for development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)