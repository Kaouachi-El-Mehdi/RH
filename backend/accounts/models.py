from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """
    Modèle utilisateur personnalisé pour le système RH
    """
    ROLE_CHOICES = [
        ('admin', _('Administrateur')),
        ('recruteur', _('Recruteur')),
        ('candidat', _('Candidat')),
    ]
    
    email = models.EmailField(_('Adresse email'), unique=True)
    role = models.CharField(
        _('Rôle'),
        max_length=20,
        choices=ROLE_CHOICES,
        default='candidat'
    )
    phone = models.CharField(
        _('Téléphone'),
        max_length=20,
        blank=True,
        null=True
    )
    birth_date = models.DateField(
        _('Date de naissance'),
        blank=True,
        null=True
    )
    address = models.TextField(
        _('Adresse'),
        blank=True,
        null=True
    )
    profile_picture = models.FileField(
        _('Photo de profil'),
        upload_to='profiles/',
        blank=True,
        null=True
    )
    is_verified = models.BooleanField(
        _('Compte vérifié'),
        default=False
    )
    created_at = models.DateTimeField(
        _('Date de création'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('Dernière modification'),
        auto_now=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = _('Utilisateur')
        verbose_name_plural = _('Utilisateurs')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def is_admin(self):
        return self.role == 'admin'

    def is_recruteur(self):
        return self.role == 'recruteur'

    def is_candidat(self):
        return self.role == 'candidat'


class UserProfile(models.Model):
    """
    Profil étendu pour les utilisateurs
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(
        _('Biographie'),
        blank=True,
        null=True
    )
    linkedin_url = models.URLField(
        _('LinkedIn'),
        blank=True,
        null=True
    )
    github_url = models.URLField(
        _('GitHub'),
        blank=True,
        null=True
    )
    website_url = models.URLField(
        _('Site web'),
        blank=True,
        null=True
    )
    skills = models.TextField(
        _('Compétences'),
        help_text=_('Séparez les compétences par des virgules'),
        blank=True,
        null=True
    )
    experience_years = models.PositiveIntegerField(
        _('Années d\'expérience'),
        default=0
    )
    education_level = models.CharField(
        _('Niveau d\'études'),
        max_length=100,
        blank=True,
        null=True
    )
    current_position = models.CharField(
        _('Poste actuel'),
        max_length=200,
        blank=True,
        null=True
    )
    current_company = models.CharField(
        _('Entreprise actuelle'),
        max_length=200,
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
    availability_date = models.DateField(
        _('Date de disponibilité'),
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _('Profil utilisateur')
        verbose_name_plural = _('Profils utilisateurs')

    def __str__(self):
        return f"Profil de {self.user.full_name}"
