from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from jobs.models import Job

User = get_user_model()


class Application(models.Model):
    """
    Candidatures pour les offres d'emploi
    """
    STATUS_CHOICES = [
        ('pending', _('En attente')),
        ('reviewing', _('En cours d\'examen')),
        ('ai_filtered', _('Filtré par IA')),
        ('shortlisted', _('Présélectionné')),
        ('interview', _('Entretien')),
        ('accepted', _('Accepté')),
        ('rejected', _('Rejeté')),
        ('withdrawn', _('Retiré')),
    ]

    candidate = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name=_('Candidat')
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name=_('Offre d\'emploi')
    )
    cv_file = models.FileField(
        _('Fichier CV'),
        upload_to='cvs/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])]
    )
    cover_letter = models.TextField(
        _('Lettre de motivation'),
        blank=True,
        null=True
    )
    status = models.CharField(
        _('Statut'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    ai_score = models.FloatField(
        _('Score IA'),
        blank=True,
        null=True,
        help_text=_('Score de pertinence calculé par l\'IA (0-100)')
    )
    ai_analysis = models.JSONField(
        _('Analyse IA'),
        blank=True,
        null=True,
        help_text=_('Détails de l\'analyse IA (compétences, expérience, etc.)')
    )
    recruiter_notes = models.TextField(
        _('Notes du recruteur'),
        blank=True,
        null=True
    )
    interview_date = models.DateTimeField(
        _('Date d\'entretien'),
        blank=True,
        null=True
    )
    salary_expectation = models.DecimalField(
        _('Prétention salariale'),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    available_from = models.DateField(
        _('Disponible à partir du'),
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        _('Date de candidature'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('Dernière modification'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('Candidature')
        verbose_name_plural = _('Candidatures')
        ordering = ['-created_at']
        unique_together = ['candidate', 'job']

    def __str__(self):
        return f"{self.candidate.full_name} - {self.job.title}"

    @property
    def is_pending(self):
        return self.status == 'pending'

    @property
    def is_ai_filtered(self):
        return self.status == 'ai_filtered'

    @property
    def is_shortlisted(self):
        return self.status == 'shortlisted'

    @property
    def ai_score_percentage(self):
        """Score IA en pourcentage"""
        if self.ai_score:
            return f"{self.ai_score:.1f}%"
        return "Non analysé"


class CVAnalysis(models.Model):
    """
    Analyse détaillée des CV par l'IA
    """
    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        related_name='analysis',
        verbose_name=_('Candidature')
    )
    extracted_text = models.TextField(
        _('Texte extrait du CV'),
        blank=True,
        null=True
    )
    extracted_skills = models.JSONField(
        _('Compétences extraites'),
        default=list,
        help_text=_('Liste des compétences identifiées par l\'IA')
    )
    extracted_experience = models.JSONField(
        _('Expérience extraite'),
        default=list,
        help_text=_('Expériences professionnelles identifiées')
    )
    extracted_education = models.JSONField(
        _('Formation extraite'),
        default=list,
        help_text=_('Formations identifiées')
    )
    skill_match_score = models.FloatField(
        _('Score de correspondance des compétences'),
        default=0.0
    )
    experience_match_score = models.FloatField(
        _('Score de correspondance de l\'expérience'),
        default=0.0
    )
    education_match_score = models.FloatField(
        _('Score de correspondance de la formation'),
        default=0.0
    )
    overall_score = models.FloatField(
        _('Score global'),
        default=0.0
    )
    ai_recommendation = models.TextField(
        _('Recommandation IA'),
        blank=True,
        null=True
    )
    keywords_found = models.JSONField(
        _('Mots-clés trouvés'),
        default=list
    )
    missing_keywords = models.JSONField(
        _('Mots-clés manquants'),
        default=list
    )
    processed_at = models.DateTimeField(
        _('Date de traitement'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('Analyse de CV')
        verbose_name_plural = _('Analyses de CV')

    def __str__(self):
        return f"Analyse - {self.application.candidate.full_name}"

    @property
    def is_recommended(self):
        """Candidat recommandé par l'IA (score > 70%)"""
        return self.overall_score >= 70

    @property
    def match_level(self):
        """Niveau de correspondance"""
        if self.overall_score >= 80:
            return "Excellent"
        elif self.overall_score >= 70:
            return "Très bon"
        elif self.overall_score >= 60:
            return "Bon"
        elif self.overall_score >= 50:
            return "Moyen"
        else:
            return "Faible"


class Interview(models.Model):
    """
    Entretiens programmés
    """
    STATUS_CHOICES = [
        ('scheduled', _('Programmé')),
        ('completed', _('Terminé')),
        ('cancelled', _('Annulé')),
        ('rescheduled', _('Reprogrammé')),
    ]

    TYPE_CHOICES = [
        ('phone', _('Téléphonique')),
        ('video', _('Visioconférence')),
        ('in_person', _('En personne')),
        ('technical', _('Technique')),
    ]

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='interviews',
        verbose_name=_('Candidature')
    )
    interviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conducted_interviews',
        verbose_name=_('Recruteur')
    )
    scheduled_date = models.DateTimeField(
        _('Date prévue')
    )
    duration_minutes = models.PositiveIntegerField(
        _('Durée (minutes)'),
        default=60
    )
    interview_type = models.CharField(
        _('Type d\'entretien'),
        max_length=20,
        choices=TYPE_CHOICES,
        default='video'
    )
    location_or_link = models.TextField(
        _('Lieu ou lien'),
        blank=True,
        null=True,
        help_text=_('Adresse physique ou lien de visioconférence')
    )
    status = models.CharField(
        _('Statut'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled'
    )
    notes = models.TextField(
        _('Notes d\'entretien'),
        blank=True,
        null=True
    )
    rating = models.PositiveIntegerField(
        _('Note sur 10'),
        blank=True,
        null=True,
        help_text=_('Note globale de 1 à 10')
    )
    feedback = models.TextField(
        _('Retour détaillé'),
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        _('Date de création'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('Dernière modification'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('Entretien')
        verbose_name_plural = _('Entretiens')
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"Entretien - {self.application.candidate.full_name} - {self.scheduled_date.strftime('%d/%m/%Y %H:%M')}"

    @property
    def is_upcoming(self):
        """Entretien à venir"""
        from django.utils import timezone
        return self.scheduled_date > timezone.now() and self.status == 'scheduled'
