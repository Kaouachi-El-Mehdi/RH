from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from candidates.models import Application

User = get_user_model()


class AIModel(models.Model):
    """
    Configuration des modèles d'IA utilisés
    """
    MODEL_TYPES = [
        ('bert', 'BERT'),
        ('gpt', 'GPT'),
        ('custom', 'Modèle personnalisé'),
    ]

    name = models.CharField(
        _('Nom du modèle'),
        max_length=100,
        unique=True
    )
    model_type = models.CharField(
        _('Type de modèle'),
        max_length=20,
        choices=MODEL_TYPES
    )
    model_path = models.CharField(
        _('Chemin du modèle'),
        max_length=500
    )
    description = models.TextField(
        _('Description'),
        blank=True,
        null=True
    )
    is_active = models.BooleanField(
        _('Modèle actif'),
        default=True
    )
    accuracy_score = models.FloatField(
        _('Score de précision'),
        blank=True,
        null=True,
        help_text=_('Score de précision sur le jeu de test')
    )
    version = models.CharField(
        _('Version'),
        max_length=20,
        default='1.0'
    )
    training_date = models.DateTimeField(
        _('Date d\'entraînement'),
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
        verbose_name = _('Modèle IA')
        verbose_name_plural = _('Modèles IA')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} v{self.version}"


class ProcessingQueue(models.Model):
    """
    File d'attente pour le traitement des CV
    """
    STATUS_CHOICES = [
        ('pending', _('En attente')),
        ('processing', _('En cours')),
        ('completed', _('Terminé')),
        ('failed', _('Échec')),
        ('retrying', _('Nouvelle tentative')),
    ]

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='processing_queue',
        verbose_name=_('Candidature')
    )
    ai_model = models.ForeignKey(
        AIModel,
        on_delete=models.CASCADE,
        related_name='processing_jobs',
        verbose_name=_('Modèle IA')
    )
    status = models.CharField(
        _('Statut'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    priority = models.PositiveIntegerField(
        _('Priorité'),
        default=1,
        help_text=_('1 = haute priorité, 5 = basse priorité')
    )
    attempts = models.PositiveIntegerField(
        _('Tentatives'),
        default=0
    )
    error_message = models.TextField(
        _('Message d\'erreur'),
        blank=True,
        null=True
    )
    processing_time = models.FloatField(
        _('Temps de traitement (secondes)'),
        blank=True,
        null=True
    )
    started_at = models.DateTimeField(
        _('Démarré à'),
        blank=True,
        null=True
    )
    completed_at = models.DateTimeField(
        _('Terminé à'),
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        _('Créé à'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('File de traitement')
        verbose_name_plural = _('Files de traitement')
        ordering = ['priority', '-created_at']

    def __str__(self):
        return f"Traitement {self.application.candidate.full_name} - {self.status}"


class SkillExtraction(models.Model):
    """
    Extraction et classification des compétences
    """
    SKILL_CATEGORIES = [
        ('technical', _('Technique')),
        ('soft', _('Relationnel')),
        ('language', _('Langue')),
        ('certification', _('Certification')),
        ('tool', _('Outil')),
        ('framework', _('Framework')),
        ('methodology', _('Méthodologie')),
    ]

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='skill_extractions',
        verbose_name=_('Candidature')
    )
    skill_name = models.CharField(
        _('Nom de la compétence'),
        max_length=100
    )
    category = models.CharField(
        _('Catégorie'),
        max_length=20,
        choices=SKILL_CATEGORIES
    )
    confidence_score = models.FloatField(
        _('Score de confiance'),
        help_text=_('Score de confiance de l\'extraction (0-1)')
    )
    context = models.TextField(
        _('Contexte'),
        blank=True,
        null=True,
        help_text=_('Phrase ou section où la compétence a été trouvée')
    )
    years_experience = models.PositiveIntegerField(
        _('Années d\'expérience'),
        blank=True,
        null=True
    )
    proficiency_level = models.CharField(
        _('Niveau de maîtrise'),
        max_length=20,
        choices=[
            ('beginner', _('Débutant')),
            ('intermediate', _('Intermédiaire')),
            ('advanced', _('Avancé')),
            ('expert', _('Expert')),
        ],
        blank=True,
        null=True
    )
    extracted_at = models.DateTimeField(
        _('Extrait à'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('Extraction de compétence')
        verbose_name_plural = _('Extractions de compétences')
        ordering = ['-confidence_score']

    def __str__(self):
        return f"{self.skill_name} ({self.confidence_score:.2f})"


class JobMatching(models.Model):
    """
    Correspondance entre candidatures et offres d'emploi
    """
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='job_matchings',
        verbose_name=_('Candidature')
    )
    skill_match_details = models.JSONField(
        _('Détails correspondance compétences'),
        default=dict,
        help_text=_('Détails de la correspondance des compétences')
    )
    experience_match_details = models.JSONField(
        _('Détails correspondance expérience'),
        default=dict
    )
    education_match_details = models.JSONField(
        _('Détails correspondance formation'),
        default=dict
    )
    location_match = models.BooleanField(
        _('Correspondance lieu'),
        default=False
    )
    salary_match = models.BooleanField(
        _('Correspondance salaire'),
        default=False
    )
    availability_match = models.BooleanField(
        _('Correspondance disponibilité'),
        default=False
    )
    overall_compatibility = models.FloatField(
        _('Compatibilité globale'),
        help_text=_('Score de compatibilité globale (0-100)')
    )
    recommendation_reason = models.TextField(
        _('Raison de la recommandation'),
        blank=True,
        null=True
    )
    red_flags = models.JSONField(
        _('Signaux d\'alerte'),
        default=list,
        help_text=_('Liste des problèmes potentiels identifiés')
    )
    calculated_at = models.DateTimeField(
        _('Calculé à'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('Correspondance emploi')
        verbose_name_plural = _('Correspondances emploi')
        ordering = ['-overall_compatibility']

    def __str__(self):
        return f"Correspondance {self.application.candidate.full_name} - {self.overall_compatibility:.1f}%"

    @property
    def is_excellent_match(self):
        return self.overall_compatibility >= 80

    @property
    def is_good_match(self):
        return 60 <= self.overall_compatibility < 80

    @property
    def is_average_match(self):
        return 40 <= self.overall_compatibility < 60


class AnalyticsReport(models.Model):
    """
    Rapports d'analyse et statistiques
    """
    REPORT_TYPES = [
        ('daily', _('Quotidien')),
        ('weekly', _('Hebdomadaire')),
        ('monthly', _('Mensuel')),
        ('custom', _('Personnalisé')),
    ]

    report_type = models.CharField(
        _('Type de rapport'),
        max_length=20,
        choices=REPORT_TYPES
    )
    title = models.CharField(
        _('Titre'),
        max_length=200
    )
    data = models.JSONField(
        _('Données du rapport'),
        default=dict
    )
    total_applications = models.PositiveIntegerField(
        _('Total candidatures'),
        default=0
    )
    ai_processed = models.PositiveIntegerField(
        _('Traitées par IA'),
        default=0
    )
    recommended_candidates = models.PositiveIntegerField(
        _('Candidats recommandés'),
        default=0
    )
    average_score = models.FloatField(
        _('Score moyen'),
        default=0.0
    )
    processing_time_avg = models.FloatField(
        _('Temps de traitement moyen'),
        default=0.0
    )
    date_from = models.DateField(
        _('Date de début')
    )
    date_to = models.DateField(
        _('Date de fin')
    )
    generated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='generated_reports',
        verbose_name=_('Généré par')
    )
    created_at = models.DateTimeField(
        _('Créé à'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('Rapport d\'analyse')
        verbose_name_plural = _('Rapports d\'analyse')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.date_from} - {self.date_to})"
