from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from candidates.models import Application
from django.db.models import Avg, Count

class DashboardStatsView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		total_applications = Application.objects.count()
		status_counts = Application.objects.values('status').annotate(count=Count('id'))
		avg_ai_score = Application.objects.aggregate(avg_score=Avg('ai_score'))['avg_score']
		recent_applications = Application.objects.order_by('-created_at')[:5]
		recent_list = [
			{
				'id': app.id,
				'candidate': str(app.candidate),
				'job': str(app.job),
				'status': app.status,
				'ai_score': app.ai_score,
				'created_at': app.created_at,
			}
			for app in recent_applications
		]
		return Response({
			'total_applications': total_applications,
			'status_counts': list(status_counts),
			'avg_ai_score': avg_ai_score,
			'recent_applications': recent_list,
		})
# Create your views here.
