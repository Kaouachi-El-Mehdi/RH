from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


class JobCategory(models.Model):
    """
    Catégories d'emplois (Informatique, Enseignement, Avocat, etc.)
    """
    name = models.CharField(
        _('Nom de la catégorie'),
        max_length=100,
        unique=True
    )
    description = models.TextField(
        _('Description'),
        blank=True,
        null=True
    )
    icon = models.CharField(
        _('Icône'),
        max_length=50,
        blank=True,
        null=True,
        help_text=_('Nom de l\'icône FontAwesome')
    )
    is_active = models.BooleanField(
        _('Actif'),
        default=True
    )
    created_at = models.DateTimeField(
        _('Date de création'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('Catégorie d\'emploi')
        verbose_name_plural = _('Catégories d\'emploi')
        ordering = ['name']

    def __str__(self):
        return self.name


class Job(models.Model):
    """
    Offres d'emploi
    """
    STATUS_CHOICES = [
        ('draft', _('Brouillon')),
        ('published', _('Publié')),
        ('closed', _('Fermé')),
        ('paused', _('En pause')),
    ]

    CONTRACT_CHOICES = [
        ('cdi', _('CDI')),
        ('cdd', _('CDD')),
        ('stage', _('Stage')),
        ('freelance', _('Freelance')),
        ('interim', _('Intérim')),
    ]

    EXPERIENCE_CHOICES = [
        ('0-1', _('0-1 an')),
        ('1-3', _('1-3 ans')),
        ('3-5', _('3-5 ans')),
        ('5-10', _('5-10 ans')),
        ('10+', _('10+ ans')),
    ]

    title = models.CharField(
        _('Titre du poste'),
        max_length=200
    )
    category = models.ForeignKey(
        JobCategory,
        on_delete=models.CASCADE,
        related_name='jobs',
        verbose_name=_('Catégorie')
    )
    company_name = models.CharField(
        _('Nom de l\'entreprise'),
        max_length=200
    )
    description = models.TextField(
        _('Description du poste')
    )
    requirements = models.TextField(
        _('Exigences du poste')
    )
    responsibilities = models.TextField(
        _('Responsabilités'),
        blank=True,
        null=True
    )
    benefits = models.TextField(
        _('Avantages'),
        blank=True,
        null=True
    )
    location = models.CharField(
        _('Lieu'),
        max_length=200
    )
    is_remote = models.BooleanField(
        _('Télétravail possible'),
        default=False
    )
    contract_type = models.CharField(
        _('Type de contrat'),
        max_length=20,
        choices=CONTRACT_CHOICES,
        default='cdi'
    )
    experience_required = models.CharField(
        _('Expérience requise'),
        max_length=10,
        choices=EXPERIENCE_CHOICES,
        default='1-3'
    )
    salary_min = models.DecimalField(
        _('Salaire minimum'),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    salary_max = models.DecimalField(
        _('Salaire maximum'),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    skills_required = models.TextField(
        _('Compétences requises'),
        help_text=_('Séparez les compétences par des virgules')
    )
    status = models.CharField(
        _('Statut'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    posted_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posted_jobs',
        verbose_name=_('Publié par')
    )
    application_deadline = models.DateTimeField(
        _('Date limite de candidature'),
        blank=True,
        null=True
    )
    max_applications = models.PositiveIntegerField(
        _('Nombre maximum de candidatures'),
        default=100
    )
    views_count = models.PositiveIntegerField(
        _('Nombre de vues'),
        default=0
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
        verbose_name = _('Offre d\'emploi')
        verbose_name_plural = _('Offres d\'emploi')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.company_name}"

    @property
    def applications_count(self):
        """Nombre de candidatures reçues"""
        return self.applications.count()

    @property
    def is_active(self):
        """Vérifie si l'offre est active"""
        return self.status == 'published'

    @property
    def salary_range(self):
        """Fourchette salariale formatée"""
        if self.salary_min and self.salary_max:
            return f"{self.salary_min:,.0f}€ - {self.salary_max:,.0f}€"
        elif self.salary_min:
            return f"À partir de {self.salary_min:,.0f}€"
        elif self.salary_max:
            return f"Jusqu'à {self.salary_max:,.0f}€"
        return "Salaire à négocier"

    def increment_views(self):
        """Incrémente le compteur de vues"""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class JobSkill(models.Model):
    """
    Compétences liées aux emplois
    """
    name = models.CharField(
        _('Nom de la compétence'),
        max_length=100,
        unique=True
    )
    category = models.ForeignKey(
        JobCategory,
        on_delete=models.CASCADE,
        related_name='skills',
        verbose_name=_('Catégorie'),
        blank=True,
        null=True
    )
    is_popular = models.BooleanField(
        _('Compétence populaire'),
        default=False
    )
    created_at = models.DateTimeField(
        _('Date de création'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('Compétence')
        verbose_name_plural = _('Compétences')
        ordering = ['name']

    def __str__(self):
        return self.name
