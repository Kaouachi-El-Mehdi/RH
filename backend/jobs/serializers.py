from rest_framework import serializers
from .models import JobCategory, Job, JobSkill
from accounts.serializers import UserSerializer


class JobCategorySerializer(serializers.ModelSerializer):
    """
    Serializer pour les catégories d'emploi
    """
    jobs_count = serializers.SerializerMethodField()

    class Meta:
        model = JobCategory
        fields = ['id', 'name', 'description', 'icon', 'is_active', 'jobs_count', 'created_at']

    def get_jobs_count(self, obj):
        return obj.jobs.filter(status='published').count()


class JobSkillSerializer(serializers.ModelSerializer):
    """
    Serializer pour les compétences
    """
    class Meta:
        model = JobSkill
        fields = ['id', 'name', 'category', 'is_popular', 'created_at']


class JobSerializer(serializers.ModelSerializer):
    """
    Serializer pour les offres d'emploi
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    posted_by_name = serializers.CharField(source='posted_by.get_full_name', read_only=True)
    applications_count = serializers.ReadOnlyField()
    salary_range = serializers.ReadOnlyField()
    skills_list = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'category', 'category_name', 'company_name',
            'description', 'requirements', 'responsibilities', 'benefits',
            'location', 'is_remote', 'contract_type', 'experience_required',
            'salary_min', 'salary_max', 'salary_range', 'skills_required',
            'skills_list', 'status', 'posted_by', 'posted_by_name',
            'application_deadline', 'max_applications', 'applications_count',
            'views_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'posted_by', 'views_count', 'created_at', 'updated_at']

    def get_skills_list(self, obj):
        """Convertit les compétences en liste"""
        if obj.skills_required:
            return [skill.strip() for skill in obj.skills_required.split(',')]
        return []

    def create(self, validated_data):
        validated_data['posted_by'] = self.context['request'].user
        return super().create(validated_data)


class JobCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour créer une offre d'emploi
    """
    class Meta:
        model = Job
        fields = [
            'title', 'category', 'company_name', 'description',
            'requirements', 'responsibilities', 'benefits',
            'location', 'is_remote', 'contract_type', 'experience_required',
            'salary_min', 'salary_max', 'skills_required', 'status',
            'application_deadline', 'max_applications'
        ]

    def create(self, validated_data):
        validated_data['posted_by'] = self.context['request'].user
        return super().create(validated_data)


class JobDetailSerializer(JobSerializer):
    """
    Serializer détaillé pour une offre d'emploi
    """
    posted_by = UserSerializer(read_only=True)
    category = JobCategorySerializer(read_only=True)
    recent_applications = serializers.SerializerMethodField()

    class Meta(JobSerializer.Meta):
        fields = JobSerializer.Meta.fields + ['recent_applications']

    def get_recent_applications(self, obj):
        """Retourne les 5 dernières candidatures"""
        from candidates.serializers import ApplicationSerializer
        recent = obj.applications.order_by('-created_at')[:5]
        return ApplicationSerializer(recent, many=True).data


class JobSearchSerializer(serializers.Serializer):
    """
    Serializer pour la recherche d'emplois
    """
    query = serializers.CharField(required=False, allow_blank=True)
    category = serializers.IntegerField(required=False)
    location = serializers.CharField(required=False, allow_blank=True)
    contract_type = serializers.CharField(required=False, allow_blank=True)
    experience_required = serializers.CharField(required=False, allow_blank=True)
    is_remote = serializers.BooleanField(required=False)
    salary_min = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    salary_max = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    skills = serializers.CharField(required=False, allow_blank=True)


class JobStatsSerializer(serializers.Serializer):
    """
    Serializer pour les statistiques des emplois
    """
    total_jobs = serializers.IntegerField()
    active_jobs = serializers.IntegerField()
    total_applications = serializers.IntegerField()
    categories_stats = serializers.ListField()
    recent_jobs = JobSerializer(many=True)
    top_skills = serializers.ListField()
