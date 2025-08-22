
from django.urls import path
from .views import NotificationListView

app_name = 'notifications'

urlpatterns = [
    path('user/', NotificationListView.as_view(), name='user-notifications'),
]
