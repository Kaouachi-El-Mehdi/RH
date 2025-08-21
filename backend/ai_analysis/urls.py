"""
URLs pour l'analyse IA des CV
"""
from django.urls import path
from . import views

app_name = 'ai_analysis'

urlpatterns = [
    # Analyse d'un CV individuel
    path('analyze/', views.upload_and_analyze_cv, name='analyze-cv'),
    
    # Analyse en lot et filtrage par domaine
    path('bulk-analyze/', views.bulk_cv_analysis, name='bulk-analyze'),
    
    # Analyse de CV spécifique pour un poste
    path('analyze-job-cvs/', views.analyze_job_cvs, name='analyze-job-cvs'),
    
    # Statut de l'IA
    path('status/', views.ai_status, name='ai-status'),
]
