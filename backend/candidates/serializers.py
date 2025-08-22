from rest_framework import serializers
from .models import Application

class ApplicationSerializer(serializers.ModelSerializer):
    candidate = serializers.PrimaryKeyRelatedField(read_only=True)
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'candidate', 'candidate_name', 'job', 'job_title', 'cv_file', 'cover_letter',
            'status', 'ai_score', 'ai_analysis', 'recruiter_notes', 'interview_date',
            'salary_expectation', 'available_from', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'ai_score', 'ai_analysis', 'candidate_name', 'job_title']
