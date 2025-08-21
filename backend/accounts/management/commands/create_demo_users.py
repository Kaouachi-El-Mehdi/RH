from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import UserProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Créer des comptes utilisateurs de démonstration'

    def handle(self, *args, **options):
        demo_users = [
            {
                'username': 'admin',
                'email': 'admin@rh.com',
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': 'System',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True
            },
            {
                'username': 'recruteur',
                'email': 'recruteur@rh.com',
                'password': 'recruteur123',
                'first_name': 'Jean',
                'last_name': 'Recruteur',
                'role': 'recruteur',
                'is_staff': False,
                'is_superuser': False
            },
            {
                'username': 'candidat',
                'email': 'candidat@rh.com',
                'password': 'candidat123',
                'first_name': 'Marie',
                'last_name': 'Candidate',
                'role': 'candidat',
                'is_staff': False,
                'is_superuser': False
            }
        ]

        for user_data in demo_users:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_staff': user_data['is_staff'],
                    'is_superuser': user_data['is_superuser'],
                }
            )
            
            if created:
                user.set_password(user_data['password'])
                user.save()
                
                # Créer ou mettre à jour le profil
                profile, profile_created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={'role': user_data['role']}
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Utilisateur créé: {user.username} ({user_data["role"]})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Utilisateur existe déjà: {user.username}')
                )

        self.stdout.write(
            self.style.SUCCESS('🎉 Comptes de démonstration créés!')
        )
