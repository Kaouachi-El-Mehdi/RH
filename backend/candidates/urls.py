from django.urls import path

app_name = 'candidates'

from . import views

urlpatterns = [
    path('applications/', views.ApplicationListView.as_view(), name='application-list'),
    path('applications/create/', views.ApplicationCreateView.as_view(), name='application-create'),
    path('applications/<int:pk>/', views.ApplicationDetailView.as_view(), name='application-detail'),
    path('stats/', views.ApplicationStatsView.as_view(), name='application-stats'),
    path('applications/<int:pk>/update-ai-score/', views.update_ai_score, name='application-update-ai-score'),
]
