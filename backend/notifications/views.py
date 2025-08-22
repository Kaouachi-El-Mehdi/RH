
from rest_framework import generics, permissions
from .models import Notification
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.views import APIView

User = get_user_model()

class NotificationListView(generics.ListAPIView):
	permission_classes = [permissions.IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		import logging
		logger = logging.getLogger('django')
		logger.warning(f"[NOTIF DEBUG] request.user: {user} | is_authenticated: {getattr(user, 'is_authenticated', None)} | id: {getattr(user, 'id', None)} | username: {getattr(user, 'username', None)}")
		if not getattr(user, 'is_authenticated', False):
			return Notification.objects.none()
		return Notification.objects.filter(recipient=user).order_by('-created_at')

	def list(self, request, *args, **kwargs):
		queryset = self.get_queryset()
		data = [
			{
				'id': n.id,
				'title': n.title,
				'message': n.message,
				'is_read': n.is_read,
				'created_at': n.created_at,
				'notification_type': n.notification_type,
				'priority': n.priority,
				'action_url': n.action_url,
				'action_label': n.action_label,
				'related_application_id': n.related_application_id,
				'related_job_id': n.related_job_id,
			}
			for n in queryset
		]
		import logging
		logger = logging.getLogger('django')
		logger.warning(f"[NOTIF DEBUG] Returned {len(data)} notifications for user id {getattr(request.user, 'id', None)}")
		return Response(data)
