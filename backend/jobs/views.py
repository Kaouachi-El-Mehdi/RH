from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q, Count
from django.utils import timezone
from .models import Job, JobCategory, JobSkill
from .serializers import (
    JobSerializer, JobDetailSerializer, JobCreateSerializer,
    JobCategorySerializer, JobSkillSerializer, JobSearchSerializer,
    JobStatsSerializer
)


class JobListView(generics.ListCreateAPIView):
    """
    Vue pour lister et créer des offres d'emploi
    """
    serializer_class = JobSerializer
    permission_classes = [AllowAny]  # Lecture libre, création pour authentifiés
    
    def get_queryset(self):
        queryset = Job.objects.filter(status='published').order_by('-created_at')
        
        # Filtres de recherche
        query = self.request.query_params.get('query', None)
        category = self.request.query_params.get('category', None)
        location = self.request.query_params.get('location', None)
        contract_type = self.request.query_params.get('contract_type', None)
        is_remote = self.request.query_params.get('is_remote', None)
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(company_name__icontains=query) |
                Q(skills_required__icontains=query)
            )
        
        if category:
            queryset = queryset.filter(category_id=category)
            
        if location:
            queryset = queryset.filter(location__icontains=location)
            
        if contract_type:
            queryset = queryset.filter(contract_type=contract_type)
            
        if is_remote == 'true':
            queryset = queryset.filter(is_remote=True)
            
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return JobCreateSerializer
        return JobSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]


class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vue pour récupérer, modifier ou supprimer une offre d'emploi
    """
    queryset = Job.objects.all()
    serializer_class = JobDetailSerializer
    permission_classes = [AllowAny]  # Lecture libre
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated()]
        return [AllowAny()]
    
    def retrieve(self, request, *args, **kwargs):
        """Incrémente le compteur de vues lors de la consultation"""
        instance = self.get_object()
        instance.increment_views()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def get_queryset(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            # Seul le créateur peut modifier/supprimer
            return Job.objects.filter(posted_by=self.request.user)
        return Job.objects.all()


class JobCategoryListView(generics.ListCreateAPIView):
    """
    Vue pour lister et créer des catégories d'emploi
    """
    queryset = JobCategory.objects.filter(is_active=True).order_by('name')
    serializer_class = JobCategorySerializer
    permission_classes = [AllowAny]
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]


class JobSkillListView(generics.ListCreateAPIView):
    """
    Vue pour lister et créer des compétences
    """
    queryset = JobSkill.objects.all().order_by('name')
    serializer_class = JobSkillSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = JobSkill.objects.all().order_by('name')
        category = self.request.query_params.get('category', None)
        popular = self.request.query_params.get('popular', None)
        
        if category:
            queryset = queryset.filter(category_id=category)
        if popular == 'true':
            queryset = queryset.filter(is_popular=True)
            
        return queryset


@api_view(['GET'])
@permission_classes([AllowAny])
def job_search(request):
    """
    Recherche avancée d'emplois
    """
    serializer = JobSearchSerializer(data=request.query_params)
    if serializer.is_valid():
        filters = Q(status='published')
        data = serializer.validated_data
        
        if data.get('query'):
            filters &= (
                Q(title__icontains=data['query']) |
                Q(description__icontains=data['query']) |
                Q(company_name__icontains=data['query']) |
                Q(skills_required__icontains=data['query'])
            )
        
        if data.get('category'):
            filters &= Q(category_id=data['category'])
            
        if data.get('location'):
            filters &= Q(location__icontains=data['location'])
            
        if data.get('contract_type'):
            filters &= Q(contract_type=data['contract_type'])
            
        if data.get('experience_required'):
            filters &= Q(experience_required=data['experience_required'])
            
        if data.get('is_remote'):
            filters &= Q(is_remote=data['is_remote'])
            
        if data.get('salary_min'):
            filters &= Q(salary_min__gte=data['salary_min'])
            
        if data.get('salary_max'):
            filters &= Q(salary_max__lte=data['salary_max'])
            
        if data.get('skills'):
            skills = [skill.strip() for skill in data['skills'].split(',')]
            for skill in skills:
                filters &= Q(skills_required__icontains=skill)
        
        jobs = Job.objects.filter(filters).order_by('-created_at')
        job_serializer = JobSerializer(jobs, many=True)
        
        return Response({
            'success': True,
            'count': jobs.count(),
            'results': job_serializer.data
        })
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def job_stats(request):
    """
    Statistiques générales des emplois
    """
    total_jobs = Job.objects.count()
    active_jobs = Job.objects.filter(status='published').count()
    
    # Stats par catégorie
    categories_stats = JobCategory.objects.annotate(
        jobs_count=Count('jobs', filter=Q(jobs__status='published'))
    ).values('id', 'name', 'jobs_count').order_by('-jobs_count')[:10]
    
    # Emplois récents
    recent_jobs = Job.objects.filter(status='published').order_by('-created_at')[:5]
    
    # Compétences populaires
    top_skills = JobSkill.objects.filter(is_popular=True).values_list('name', flat=True)[:10]
    
    # Total candidatures
    from candidates.models import Application
    total_applications = Application.objects.count()
    
    stats_data = {
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'categories_stats': list(categories_stats),
        'recent_jobs': JobSerializer(recent_jobs, many=True).data,
        'top_skills': list(top_skills)
    }
    
    return Response({
        'success': True,
        'stats': stats_data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_jobs(request):
    """
    Mes offres d'emploi (pour les recruteurs)
    """
    jobs = Job.objects.filter(posted_by=request.user).order_by('-created_at')
    serializer = JobSerializer(jobs, many=True)
    
    return Response({
        'success': True,
        'count': jobs.count(),
        'results': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def publish_job(request, job_id):
    """
    Publier une offre d'emploi
    """
    try:
        job = Job.objects.get(id=job_id, posted_by=request.user)
        job.status = 'published'
        job.save()
        
        return Response({
            'success': True,
            'message': 'Offre publiée avec succès'
        })
    except Job.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Offre non trouvée'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def close_job(request, job_id):
    """
    Fermer une offre d'emploi
    """
    try:
        job = Job.objects.get(id=job_id, posted_by=request.user)
        job.status = 'closed'
        job.save()
        
        return Response({
            'success': True,
            'message': 'Offre fermée avec succès'
        })
    except Job.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Offre non trouvée'
        }, status=status.HTTP_404_NOT_FOUND)
