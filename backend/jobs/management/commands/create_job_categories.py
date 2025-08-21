from django.core.management.base import BaseCommand
from jobs.models import JobCategory


class Command(BaseCommand):
    help = 'Créer les catégories d\'emploi par défaut'

    def handle(self, *args, **options):
        categories = [
            {'name': 'Information Technology', 'description': 'Développement, IT, Software'},
            {'name': 'Teaching', 'description': 'Éducation, Formation, Enseignement'},
            {'name': 'Advocacy', 'description': 'Droit, Juridique, Avocat'},
            {'name': 'Accounting', 'description': 'Comptabilité, Finance, Audit'},
            {'name': 'Engineering', 'description': 'Ingénierie, Technique'},
            {'name': 'Healthcare', 'description': 'Santé, Médical, Soins'},
            {'name': 'Banking', 'description': 'Banque, Finance, Assurance'},
            {'name': 'Sales', 'description': 'Vente, Commercial'},
            {'name': 'Marketing', 'description': 'Marketing, Communication'},
            {'name': 'Human Resources', 'description': 'RH, Ressources Humaines'},
            {'name': 'Consulting', 'description': 'Conseil, Consulting'},
            {'name': 'Design', 'description': 'Design, Créatif, Graphisme'},
            {'name': 'Chef', 'description': 'Cuisine, Restauration'},
        ]

        for cat_data in categories:
            category, created = JobCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Catégorie créée: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Catégorie existe déjà: {category.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('✅ Catégories d\'emploi initialisées!')
        )
