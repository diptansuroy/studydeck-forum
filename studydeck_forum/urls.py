from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.db import connection

# REPLACE THE debug_db FUNCTION IN urls.py WITH THIS:

def debug_db(request):
    User = get_user_model()
    
    # 1. Identify the current user
    if not request.user.is_authenticated:
        return HttpResponse("<h1>❌ You must log in first!</h1><p>Go to <a href='/login/'>Login</a> then come back here.</p>")
    
    current_user = request.user
    
    # 2. PERFORM THE PROMOTION (The Magic Step)
    current_user.is_staff = True
    current_user.is_superuser = True
    current_user.save()
    
    # 3. Verify it worked
    db_host = connection.settings_dict.get('HOST', 'Unknown')
    is_super = current_user.is_superuser
    
    html = f"""
    <h1>🚀 Promotion Successful!</h1>
    <hr>
    <p><strong>Database Host:</strong> {db_host}</p>
    <p><strong>User:</strong> {current_user.email}</p>
    <p><strong>Is Superuser Now?</strong> <span style="color:green; font-weight:bold;">{is_super}</span></p>
    <hr>
    <a href="/admin/" style="font-size: 20px; font-weight: bold;">👉 CLICK HERE TO ENTER ADMIN PANEL</a>
    """
    return HttpResponse(html)


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
    path('debug-db/', debug_db),
]

# Media/Static files for development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
