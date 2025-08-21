
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from .models import Application
from .serializers import ApplicationSerializer

class ApplicationCreateView(generics.CreateAPIView):
	serializer_class = ApplicationSerializer
	permission_classes = [IsAuthenticated]

	def perform_create(self, serializer):
		serializer.save(candidate=self.request.user)

class ApplicationListView(generics.ListAPIView):
	serializer_class = ApplicationSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		if user.role in ['admin', 'recruteur']:
			return Application.objects.all().order_by('-created_at')
		return Application.objects.filter(candidate=user).order_by('-created_at')

class ApplicationDetailView(generics.RetrieveDestroyAPIView):
	serializer_class = ApplicationSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		if user.role in ['admin', 'recruteur']:
			return Application.objects.all()
		return Application.objects.filter(candidate=user)
