"""
Commande Django pour entraîner l'IA de filtrage de CV
Usage: python manage.py train_cv_ai --dataset /path/to/your/cv/dataset
"""
from django.core.management.base import BaseCommand, CommandError
from ai_analysis.cv_processor import CVAnalyzer
import os
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Entraîne les modèles IA pour le filtrage automatique de CV'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dataset',
            type=str,
            required=True,
            help='Chemin vers le dossier contenant vos CV pour l\'entraînement'
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Exécute des tests après l\'entraînement'
        )

    def handle(self, *args, **options):
        dataset_path = options['dataset']
        run_tests = options['test']
        
        self.stdout.write(
            self.style.SUCCESS('🚀 Début de l\'entraînement des modèles IA')
        )
        
        if not os.path.exists(dataset_path):
            raise CommandError(f'Le dossier {dataset_path} n\'existe pas!')
        
        # Initialiser l'analyseur
        analyzer = CVAnalyzer()
        
        # Traitement du dataset
        self.stdout.write('📄 Traitement des CV du dataset...')
        cv_dataframe = analyzer.process_cv_dataset(dataset_path)
        
        if cv_dataframe.empty:
            raise CommandError('Aucun CV trouvé dans le dataset!')
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ {len(cv_dataframe)} CV traités avec succès')
        )
        
        # Afficher les statistiques
        self.display_dataset_stats(cv_dataframe)
        
        # Entraîner les modèles
        self.stdout.write('🤖 Entraînement des modèles d\'IA...')
        trained_df = analyzer.train_models(cv_dataframe)
        
        # Sauvegarder les modèles
        models_path = "C:/Users/Me/Desktop/RH/ai-model"
        analyzer.save_models(models_path)
        
        # Sauvegarder les données d'entraînement
        data_path = "C:/Users/Me/Desktop/RH/data/training_data.csv"
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        trained_df.to_csv(data_path, index=False, encoding='utf-8')
        
        self.stdout.write(
            self.style.SUCCESS('✅ ENTRAÎNEMENT TERMINÉ AVEC SUCCÈS!')
        )
        
        # Tests optionnels
        if run_tests:
            self.run_filtering_tests(analyzer, trained_df)
    
    def display_dataset_stats(self, cv_dataframe):
        """Affiche les statistiques du dataset"""
        self.stdout.write('\n📊 STATISTIQUES DU DATASET:')
        self.stdout.write(f'   Nombre total de CV: {len(cv_dataframe)}')
        
        domains = cv_dataframe['domain'].value_counts()
        self.stdout.write('   Répartition par domaine:')
        for domain, count in domains.items():
            self.stdout.write(f'     - {domain}: {count} CV')
        
        avg_experience = cv_dataframe['experience_years'].mean()
        self.stdout.write(f'   Expérience moyenne: {avg_experience:.1f} ans')
        
        avg_skills = cv_dataframe['skills_count'].mean()
        self.stdout.write(f'   Compétences moyennes par CV: {avg_skills:.1f}')
    
    def run_filtering_tests(self, analyzer, cv_dataframe):
        """Exécute des tests de filtrage"""
        self.stdout.write('\n🧪 Tests du système de filtrage...')
        
        # Analyser tous les CV
        cv_analyses = []
        for idx, row in cv_dataframe.iterrows():
            analysis = analyzer.analyze_cv(row['raw_text'])
            analysis['filename'] = row['filename']
            cv_analyses.append(analysis)
        
        # Test pour chaque domaine
        domains = ['informatique', 'enseignement', 'avocat', 'marketing', 'finance']
        
        for domain in domains:
            top_candidates = analyzer.filter_top_candidates(cv_analyses, domain, 5)
            if top_candidates:
                self.stdout.write(f'\n🔍 Top 5 candidats pour {domain}:')
                for i, candidate in enumerate(top_candidates, 1):
                    self.stdout.write(
                        f'   {i}. {candidate["filename"]} - Score: {candidate["quality_score"]:.1f}'
                    )
