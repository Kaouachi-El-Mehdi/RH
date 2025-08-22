from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
# Endpoint to update AI score for an application
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_ai_score(request, pk):
	try:
		application = Application.objects.get(pk=pk)
	except Application.DoesNotExist:
		return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)
	score = request.data.get('ai_score')
	if score is None:
		return Response({'error': 'ai_score is required'}, status=status.HTTP_400_BAD_REQUEST)
	try:
		application.ai_score = float(score)
		application.save()
		return Response({'success': True, 'ai_score': application.ai_score})
	except Exception as e:
		return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from django.db.models import Avg, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg, Count
from rest_framework.permissions import IsAuthenticated
# Dashboard stats view
class ApplicationStatsView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		user = request.user
		qs = Application.objects.all()
		if user.role == 'candidat':
			qs = qs.filter(candidate=user)
		elif user.role == 'recruteur':
			qs = qs.filter(job__posted_by=user)
		# Stats
		total = qs.count()
		by_status = qs.values('status').annotate(count=Count('id'))
		avg_score = qs.aggregate(avg=Avg('ai_score'))['avg']
		recent = list(qs.order_by('-created_at')[:5].values('id', 'job__title', 'status', 'ai_score', 'created_at'))

		# Average AI score per job
		jobs_scores = qs.values('job__id', 'job__title').annotate(avg_score=Avg('ai_score'), count=Count('id')).order_by('-count')

		return Response({
			'total': total,
			'by_status': list(by_status),
			'avg_score': avg_score,
			'recent': recent,
			'jobs_scores': list(jobs_scores),
		})
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from .models import Application
from .serializers import ApplicationSerializer

class ApplicationCreateView(generics.CreateAPIView):
	serializer_class = ApplicationSerializer
	permission_classes = [IsAuthenticated]

	def perform_create(self, serializer):
		application = serializer.save(candidate=self.request.user)
		# Create notification for recruiter
		from notifications.models import Notification
		job = application.job
		recruiter = getattr(job, 'posted_by', None)
		if recruiter:
			Notification.objects.create(
				recipient=recruiter,
				title=f"Nouvelle candidature pour {job.title}",
				message=f"{self.request.user.get_full_name()} a postulé à l'offre {job.title}.",
				notification_type='info',
				priority='normal',
				related_application=application,
				related_job=job
			)

class ApplicationListView(generics.ListAPIView):
	serializer_class = ApplicationSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		if user.role in ['admin', 'recruteur']:
			return Application.objects.all().order_by('-created_at')
		return Application.objects.filter(candidate=user).order_by('-created_at')


	def perform_update(self, serializer):
		old_instance = self.get_object()
		old_status = old_instance.status
		instance = serializer.save()
		# If status changed, notify candidate
		if instance.status != old_status:
			from notifications.models import Notification
			Notification.objects.create(
				recipient=instance.candidate,
				title=f"Mise à jour de votre candidature pour {instance.job.title}",
				message=f"Statut mis à jour: {instance.status}",
				notification_type='info',
				priority='normal',
				related_application=instance,
				related_job=instance.job
			)
class ApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
	serializer_class = ApplicationSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		if user.role in ['admin', 'recruteur']:
			return Application.objects.all()
		return Application.objects.filter(candidate=user)
