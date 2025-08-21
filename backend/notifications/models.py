from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from candidates.models import Application
from jobs.models import Job

User = get_user_model()


class NotificationTemplate(models.Model):
    """
    Templates pour les notifications email
    """
    TEMPLATE_TYPES = [
        ('application_received', _('Candidature reçue')),
        ('application_status_update', _('Mise à jour statut candidature')),
        ('interview_scheduled', _('Entretien programmé')),
        ('interview_reminder', _('Rappel entretien')),
        ('job_published', _('Offre publiée')),
        ('weekly_summary', _('Résumé hebdomadaire')),
        ('ai_analysis_complete', _('Analyse IA terminée')),
    ]

    name = models.CharField(
        _('Nom du template'),
        max_length=100,
        unique=True
    )
    template_type = models.CharField(
        _('Type de template'),
        max_length=30,
        choices=TEMPLATE_TYPES
    )
    subject = models.CharField(
        _('Sujet'),
        max_length=200
    )
    html_content = models.TextField(
        _('Contenu HTML')
    )
    text_content = models.TextField(
        _('Contenu texte'),
        blank=True,
        null=True
    )
    variables = models.JSONField(
        _('Variables disponibles'),
        default=list,
        help_text=_('Liste des variables utilisables dans le template')
    )
    is_active = models.BooleanField(
        _('Actif'),
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
        verbose_name = _('Template de notification')
        verbose_name_plural = _('Templates de notification')
        ordering = ['name']

    def __str__(self):
        return self.name


class Notification(models.Model):
    """
    Notifications système (in-app)
    """
    NOTIFICATION_TYPES = [
        ('info', _('Information')),
        ('success', _('Succès')),
        ('warning', _('Attention')),
        ('error', _('Erreur')),
    ]

    PRIORITY_CHOICES = [
        ('low', _('Basse')),
        ('normal', _('Normale')),
        ('high', _('Haute')),
        ('urgent', _('Urgente')),
    ]

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Destinataire')
    )
    title = models.CharField(
        _('Titre'),
        max_length=200
    )
    message = models.TextField(
        _('Message')
    )
    notification_type = models.CharField(
        _('Type'),
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='info'
    )
    priority = models.CharField(
        _('Priorité'),
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='normal'
    )
    is_read = models.BooleanField(
        _('Lu'),
        default=False
    )
    action_url = models.URLField(
        _('URL d\'action'),
        blank=True,
        null=True,
        help_text=_('URL vers laquelle rediriger lors du clic')
    )
    action_label = models.CharField(
        _('Libellé action'),
        max_length=50,
        blank=True,
        null=True
    )
    related_application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='notifications',
        verbose_name=_('Candidature liée')
    )
    related_job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='notifications',
        verbose_name=_('Offre liée')
    )
    expires_at = models.DateTimeField(
        _('Expire à'),
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        _('Créée à'),
        auto_now_add=True
    )
    read_at = models.DateTimeField(
        _('Lue à'),
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']

    def __str__(self):
        status = "✓" if self.is_read else "●"
        return f"{status} {self.title} - {self.recipient.full_name}"

    def mark_as_read(self):
        """Marquer comme lue"""
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=['is_read', 'read_at'])


class EmailNotification(models.Model):
    """
    Notifications email envoyées
    """
    STATUS_CHOICES = [
        ('pending', _('En attente')),
        ('sent', _('Envoyé')),
        ('failed', _('Échec')),
        ('bounced', _('Rebondi')),
        ('delivered', _('Délivré')),
        ('opened', _('Ouvert')),
        ('clicked', _('Cliqué')),
    ]

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='email_notifications',
        verbose_name=_('Destinataire')
    )
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.CASCADE,
        related_name='sent_emails',
        verbose_name=_('Template utilisé')
    )
    subject = models.CharField(
        _('Sujet'),
        max_length=200
    )
    html_content = models.TextField(
        _('Contenu HTML')
    )
    text_content = models.TextField(
        _('Contenu texte'),
        blank=True,
        null=True
    )
    status = models.CharField(
        _('Statut'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    email_id = models.CharField(
        _('ID Email'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('ID fourni par le service d\'envoi')
    )
    error_message = models.TextField(
        _('Message d\'erreur'),
        blank=True,
        null=True
    )
    attempts = models.PositiveIntegerField(
        _('Tentatives'),
        default=0
    )
    related_application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='email_notifications',
        verbose_name=_('Candidature liée')
    )
    related_job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='email_notifications',
        verbose_name=_('Offre liée')
    )
    scheduled_at = models.DateTimeField(
        _('Programmé à'),
        blank=True,
        null=True
    )
    sent_at = models.DateTimeField(
        _('Envoyé à'),
        blank=True,
        null=True
    )
    delivered_at = models.DateTimeField(
        _('Délivré à'),
        blank=True,
        null=True
    )
    opened_at = models.DateTimeField(
        _('Ouvert à'),
        blank=True,
        null=True
    )
    clicked_at = models.DateTimeField(
        _('Cliqué à'),
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        _('Créé à'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('Notification email')
        verbose_name_plural = _('Notifications email')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} - {self.recipient.email} ({self.status})"

    @property
    def is_successful(self):
        return self.status in ['sent', 'delivered', 'opened', 'clicked']


class NotificationPreference(models.Model):
    """
    Préférences de notification des utilisateurs
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
        verbose_name=_('Utilisateur')
    )
    
    # Notifications email
    email_application_received = models.BooleanField(
        _('Email - Candidature reçue'),
        default=True
    )
    email_application_status_update = models.BooleanField(
        _('Email - Mise à jour candidature'),
        default=True
    )
    email_interview_scheduled = models.BooleanField(
        _('Email - Entretien programmé'),
        default=True
    )
    email_interview_reminder = models.BooleanField(
        _('Email - Rappel entretien'),
        default=True
    )
    email_weekly_summary = models.BooleanField(
        _('Email - Résumé hebdomadaire'),
        default=False
    )
    
    # Notifications in-app
    inapp_application_received = models.BooleanField(
        _('App - Candidature reçue'),
        default=True
    )
    inapp_application_status_update = models.BooleanField(
        _('App - Mise à jour candidature'),
        default=True
    )
    inapp_interview_scheduled = models.BooleanField(
        _('App - Entretien programmé'),
        default=True
    )
    inapp_ai_analysis_complete = models.BooleanField(
        _('App - Analyse IA terminée'),
        default=True
    )
    
    # Paramètres généraux
    digest_frequency = models.CharField(
        _('Fréquence du digest'),
        max_length=20,
        choices=[
            ('never', _('Jamais')),
            ('daily', _('Quotidien')),
            ('weekly', _('Hebdomadaire')),
            ('monthly', _('Mensuel')),
        ],
        default='weekly'
    )
    quiet_hours_start = models.TimeField(
        _('Début heures silencieuses'),
        blank=True,
        null=True,
        help_text=_('Pas de notifications pendant ces heures')
    )
    quiet_hours_end = models.TimeField(
        _('Fin heures silencieuses'),
        blank=True,
        null=True
    )
    timezone = models.CharField(
        _('Fuseau horaire'),
        max_length=50,
        default='Europe/Paris'
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
        verbose_name = _('Préférence de notification')
        verbose_name_plural = _('Préférences de notification')

    def __str__(self):
        return f"Préférences - {self.user.full_name}"
