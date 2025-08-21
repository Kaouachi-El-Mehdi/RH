from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from jobs.models import Job, JobCategory

User = get_user_model()


class DashboardWidget(models.Model):
    """
    Widgets configurables pour le tableau de bord
    """
    WIDGET_TYPES = [
        ('metric', _('Métrique')),
        ('chart', _('Graphique')),
        ('table', _('Tableau')),
        ('progress', _('Barre de progression')),
        ('list', _('Liste')),
        ('calendar', _('Calendrier')),
    ]

    name = models.CharField(
        _('Nom du widget'),
        max_length=100
    )
    widget_type = models.CharField(
        _('Type de widget'),
        max_length=20,
        choices=WIDGET_TYPES
    )
    title = models.CharField(
        _('Titre affiché'),
        max_length=200
    )
    description = models.TextField(
        _('Description'),
        blank=True,
        null=True
    )
    config = models.JSONField(
        _('Configuration'),
        default=dict,
        help_text=_('Configuration spécifique au widget')
    )
    query = models.TextField(
        _('Requête de données'),
        blank=True,
        null=True,
        help_text=_('Requête SQL ou configuration pour récupérer les données')
    )
    refresh_interval = models.PositiveIntegerField(
        _('Intervalle de rafraîchissement (minutes)'),
        default=60
    )
    is_active = models.BooleanField(
        _('Actif'),
        default=True
    )
    order = models.PositiveIntegerField(
        _('Ordre d\'affichage'),
        default=0
    )
    created_at = models.DateTimeField(
        _('Créé à'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('Modifié à'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('Widget de tableau de bord')
        verbose_name_plural = _('Widgets de tableau de bord')
        ordering = ['order', 'name']

    def __str__(self):
        return self.title


class UserDashboard(models.Model):
    """
    Configuration du tableau de bord par utilisateur
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='dashboard_config',
        verbose_name=_('Utilisateur')
    )
    widgets = models.ManyToManyField(
        DashboardWidget,
        through='UserDashboardWidget',
        verbose_name=_('Widgets')
    )
    layout = models.JSONField(
        _('Configuration de mise en page'),
        default=dict,
        help_text=_('Position et taille des widgets')
    )
    theme = models.CharField(
        _('Thème'),
        max_length=20,
        choices=[
            ('light', _('Clair')),
            ('dark', _('Sombre')),
            ('auto', _('Automatique')),
        ],
        default='light'
    )
    auto_refresh = models.BooleanField(
        _('Rafraîchissement automatique'),
        default=True
    )
    created_at = models.DateTimeField(
        _('Créé à'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('Modifié à'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('Tableau de bord utilisateur')
        verbose_name_plural = _('Tableaux de bord utilisateur')

    def __str__(self):
        return f"Dashboard - {self.user.full_name}"


class UserDashboardWidget(models.Model):
    """
    Relation entre utilisateur et widgets avec configuration
    """
    user_dashboard = models.ForeignKey(
        UserDashboard,
        on_delete=models.CASCADE
    )
    widget = models.ForeignKey(
        DashboardWidget,
        on_delete=models.CASCADE
    )
    position_x = models.PositiveIntegerField(
        _('Position X'),
        default=0
    )
    position_y = models.PositiveIntegerField(
        _('Position Y'),
        default=0
    )
    width = models.PositiveIntegerField(
        _('Largeur'),
        default=4
    )
    height = models.PositiveIntegerField(
        _('Hauteur'),
        default=3
    )
    is_visible = models.BooleanField(
        _('Visible'),
        default=True
    )
    custom_config = models.JSONField(
        _('Configuration personnalisée'),
        default=dict,
        blank=True
    )

    class Meta:
        verbose_name = _('Widget utilisateur')
        verbose_name_plural = _('Widgets utilisateur')
        unique_together = ['user_dashboard', 'widget']

    def __str__(self):
        return f"{self.user_dashboard.user.full_name} - {self.widget.title}"


class RecruitmentStats(models.Model):
    """
    Statistiques de recrutement agrégées
    """
    PERIOD_TYPES = [
        ('daily', _('Quotidien')),
        ('weekly', _('Hebdomadaire')),
        ('monthly', _('Mensuel')),
        ('quarterly', _('Trimestriel')),
        ('yearly', _('Annuel')),
    ]

    date = models.DateField(
        _('Date')
    )
    period_type = models.CharField(
        _('Type de période'),
        max_length=20,
        choices=PERIOD_TYPES
    )
    job_category = models.ForeignKey(
        JobCategory,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='stats',
        verbose_name=_('Catégorie d\'emploi')
    )
    
    # Statistiques des offres
    jobs_published = models.PositiveIntegerField(
        _('Offres publiées'),
        default=0
    )
    jobs_closed = models.PositiveIntegerField(
        _('Offres fermées'),
        default=0
    )
    active_jobs = models.PositiveIntegerField(
        _('Offres actives'),
        default=0
    )
    
    # Statistiques des candidatures
    total_applications = models.PositiveIntegerField(
        _('Total candidatures'),
        default=0
    )
    new_applications = models.PositiveIntegerField(
        _('Nouvelles candidatures'),
        default=0
    )
    ai_processed_applications = models.PositiveIntegerField(
        _('Candidatures traitées par IA'),
        default=0
    )
    shortlisted_applications = models.PositiveIntegerField(
        _('Candidatures présélectionnées'),
        default=0
    )
    interviews_scheduled = models.PositiveIntegerField(
        _('Entretiens programmés'),
        default=0
    )
    interviews_completed = models.PositiveIntegerField(
        _('Entretiens terminés'),
        default=0
    )
    hires_made = models.PositiveIntegerField(
        _('Embauches réalisées'),
        default=0
    )
    
    # Scores et métriques
    average_ai_score = models.FloatField(
        _('Score IA moyen'),
        default=0.0
    )
    average_processing_time = models.FloatField(
        _('Temps de traitement moyen (minutes)'),
        default=0.0
    )
    conversion_rate = models.FloatField(
        _('Taux de conversion (%)'),
        default=0.0,
        help_text=_('Pourcentage de candidatures aboutissant à une embauche')
    )
    
    # Données détaillées
    detailed_stats = models.JSONField(
        _('Statistiques détaillées'),
        default=dict,
        help_text=_('Données supplémentaires pour les graphiques')
    )
    
    created_at = models.DateTimeField(
        _('Créé à'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('Modifié à'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('Statistique de recrutement')
        verbose_name_plural = _('Statistiques de recrutement')
        ordering = ['-date']
        unique_together = ['date', 'period_type', 'job_category']

    def __str__(self):
        category = f" - {self.job_category.name}" if self.job_category else ""
        return f"Stats {self.get_period_type_display()} {self.date}{category}"


class PerformanceMetric(models.Model):
    """
    Métriques de performance du système
    """
    METRIC_TYPES = [
        ('ai_accuracy', _('Précision IA')),
        ('processing_speed', _('Vitesse de traitement')),
        ('user_satisfaction', _('Satisfaction utilisateur')),
        ('system_uptime', _('Disponibilité système')),
        ('api_response_time', _('Temps de réponse API')),
    ]

    name = models.CharField(
        _('Nom de la métrique'),
        max_length=100
    )
    metric_type = models.CharField(
        _('Type de métrique'),
        max_length=30,
        choices=METRIC_TYPES
    )
    value = models.FloatField(
        _('Valeur')
    )
    unit = models.CharField(
        _('Unité'),
        max_length=20,
        blank=True,
        null=True
    )
    target_value = models.FloatField(
        _('Valeur cible'),
        blank=True,
        null=True
    )
    description = models.TextField(
        _('Description'),
        blank=True,
        null=True
    )
    metadata = models.JSONField(
        _('Métadonnées'),
        default=dict,
        blank=True
    )
    measured_at = models.DateTimeField(
        _('Mesuré à'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('Métrique de performance')
        verbose_name_plural = _('Métriques de performance')
        ordering = ['-measured_at']

    def __str__(self):
        unit = f" {self.unit}" if self.unit else ""
        return f"{self.name}: {self.value}{unit}"

    @property
    def is_on_target(self):
        """Vérifie si la métrique atteint la valeur cible"""
        if self.target_value:
            return self.value >= self.target_value
        return None

    @property
    def performance_percentage(self):
        """Pourcentage de performance par rapport à la cible"""
        if self.target_value and self.target_value > 0:
            return (self.value / self.target_value) * 100
        return None
