from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.db import connection

def debug_db(request):
    User = get_user_model()
    # 1. Get Database Connection Info
    db_host = connection.settings_dict.get('HOST', 'Unknown')
    db_name = connection.settings_dict.get('NAME', 'Unknown')
    
    # 2. List all Superusers in THIS database
    supers = list(User.objects.filter(is_superuser=True).values_list('email', flat=True))
    
    # 3. Check YOUR status
    status = "Not logged in"
    if request.user.is_authenticated:
        status = f"Logged in as: {request.user.email} <br> Is Superuser? {request.user.is_superuser} <br> Is Staff? {request.user.is_staff}"
        
    html = f"""
    <h1>🕵️‍♂️ Database Detective</h1>
    <hr>
    <h3>1. Connection Info</h3>
    <p><strong>Host:</strong> {db_host}</p>
    <p><strong>Name:</strong> {db_name}</p>
    <hr>
    <h3>2. Superusers Found in THIS DB</h3>
    <p>{supers}</p>
    <hr>
    <h3>3. Who are you?</h3>
    <p>{status}</p>
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
