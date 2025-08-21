"""
URL configuration for rh_management project.
Système de gestion RH avec IA
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    API Root - Point d'entrée principal de l'API RH Management
    """
    return Response({
        'message': 'Bienvenue sur l\'API RH Management avec IA',
        'version': '1.0.0',
        'status': 'API is running successfully!',
        'endpoints': {
            'auth': {
                'register': '/api/auth/register/',
                'login': '/api/auth/login/',
                'logout': '/api/auth/logout/',
                'profile': '/api/auth/profile/',
            },
            'jobs': {
                'list': '/api/jobs/',
                'search': '/api/jobs/search/',
                'stats': '/api/jobs/stats/',
                'categories': '/api/jobs/categories/',
                'skills': '/api/jobs/skills/',
            },
            'candidates': {
                'applications': '/api/candidates/applications/',
                'upload_cv': '/api/candidates/upload-cv/',
                'analyze': '/api/candidates/analyze/',
            },
            'admin': '/admin/',
            'docs': '/api/docs/'
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def api_status(request):
    """
    API Status - Vérification du statut de l'API
    """
    return Response({
        'status': 'OK',
        'message': 'L\'API RH Management fonctionne correctement',
        'database': 'PostgreSQL connectée',
        'authentication': 'JWT configuré',
        'features': [
            'Gestion des utilisateurs',
            'Gestion des offres d\'emploi',
            'Upload de CV (en développement)',
            'Analyse IA (en développement)'
        ]
    })


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Root
    path('api/', api_root, name='api-root'),
    path('api/status/', api_status, name='api-status'),
    
    # API Endpoints
    path('api/auth/', include('accounts.urls')),
    path('api/jobs/', include('jobs.urls')),
    path('api/candidates/', include('candidates.urls')),
    path('api/ai/', include('ai_analysis.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/dashboard/', include('dashboard.urls')),
]

# Servir les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
