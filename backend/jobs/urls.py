from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Offres d'emploi
    path('', views.JobListView.as_view(), name='job-list'),
    path('<int:pk>/', views.JobDetailView.as_view(), name='job-detail'),
    path('search/', views.job_search, name='job-search'),
    path('stats/', views.job_stats, name='job-stats'),
    path('my-jobs/', views.my_jobs, name='my-jobs'),
    
    # Actions sur les emplois
    path('<int:job_id>/publish/', views.publish_job, name='publish-job'),
    path('<int:job_id>/close/', views.close_job, name='close-job'),
    
    # Catégories et compétences
    path('categories/', views.JobCategoryListView.as_view(), name='category-list'),
    path('skills/', views.JobSkillListView.as_view(), name='skill-list'),
]
