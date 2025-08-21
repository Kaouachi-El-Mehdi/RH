from django.urls import path

app_name = 'candidates'

from . import views

urlpatterns = [
    path('applications/', views.ApplicationListView.as_view(), name='application-list'),
    path('applications/create/', views.ApplicationCreateView.as_view(), name='application-create'),
    path('applications/<int:pk>/', views.ApplicationDetailView.as_view(), name='application-detail'),
]
