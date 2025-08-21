"""
Script d'entraînement pour l'IA de filtrage de CV
Utilise votre dataset existant pour entraîner les modèles
"""
import os
import sys
import django
from pathlib import Path

# Configuration Django
sys.path.append(str(Path(__file__).parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rh_management.settings')
django.setup()

from ai_analysis.cv_processor import CVAnalyzer
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def train_ai_models(dataset_path: str):
    """
    Entraîne les modèles IA avec votre dataset de CV
    
    Args:
        dataset_path: Chemin vers votre dossier contenant les CV
    """
    
    if not os.path.exists(dataset_path):
        logger.error(f"Le dossier {dataset_path} n'existe pas!")
        return
    
    logger.info("🚀 Début de l'entraînement des modèles IA pour le filtrage de CV")
    logger.info(f"📁 Dataset: {dataset_path}")
    
    # Initialiser l'analyseur
    analyzer = CVAnalyzer()
    
    # Traitement du dataset
    logger.info("📄 Traitement des CV du dataset...")
    cv_dataframe = analyzer.process_cv_dataset(dataset_path)
    
    if cv_dataframe.empty:
        logger.error("Aucun CV trouvé dans le dataset!")
        return
    
    logger.info(f"✅ {len(cv_dataframe)} CV traités avec succès")
    
    # Afficher les statistiques du dataset
    logger.info("\n📊 STATISTIQUES DU DATASET:")
    logger.info(f"   Nombre total de CV: {len(cv_dataframe)}")
    
    domains = cv_dataframe['domain'].value_counts()
    logger.info("   Répartition par domaine:")
    for domain, count in domains.items():
        logger.info(f"     - {domain}: {count} CV")
    
    avg_experience = cv_dataframe['experience_years'].mean()
    logger.info(f"   Expérience moyenne: {avg_experience:.1f} ans")
    
    avg_skills = cv_dataframe['skills_count'].mean()
    logger.info(f"   Compétences moyennes par CV: {avg_skills:.1f}")
    
    # Entraîner les modèles
    logger.info("\n🤖 Entraînement des modèles d'IA...")
    trained_df = analyzer.train_models(cv_dataframe)
    
    # Sauvegarder les modèles
    models_path = "C:/Users/Me/Desktop/RH/ai-model"
    analyzer.save_models(models_path)
    
    # Sauvegarder les données d'entraînement
    data_path = "C:/Users/Me/Desktop/RH/data/training_data.csv"
    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    trained_df.to_csv(data_path, index=False, encoding='utf-8')
    logger.info(f"💾 Données d'entraînement sauvegardées: {data_path}")
    
    # Test rapide du modèle
    logger.info("\n🧪 Test du modèle entraîné...")
    sample_cv = trained_df.iloc[0]['raw_text']
    analysis = analyzer.analyze_cv(sample_cv)
    
    logger.info("   Résultat du test:")
    logger.info(f"     - Domaine prédit: {analysis['domain']}")
    logger.info(f"     - Confiance: {analysis['domain_confidence']:.2f}")
    logger.info(f"     - Score qualité: {analysis['quality_score']:.1f}")
    logger.info(f"     - Compétences: {analysis['skills_count']}")
    
    logger.info("\n✅ ENTRAÎNEMENT TERMINÉ AVEC SUCCÈS!")
    logger.info("🎯 L'IA est maintenant prête pour le filtrage automatique des CV")
    
    return analyzer, trained_df

def test_filtering(analyzer, cv_dataframe, domain="informatique", top_n=10):
    """Test du système de filtrage"""
    logger.info(f"\n🔍 Test du filtrage - Top {top_n} candidats en {domain}")
    
    # Analyser tous les CV
    cv_analyses = []
    for idx, row in cv_dataframe.iterrows():
        analysis = analyzer.analyze_cv(row['raw_text'])
        analysis['filename'] = row['filename']
        cv_analyses.append(analysis)
    
    # Filtrer les top candidats
    top_candidates = analyzer.filter_top_candidates(cv_analyses, domain, top_n)
    
    logger.info(f"📋 Top {len(top_candidates)} candidats pour {domain}:")
    for i, candidate in enumerate(top_candidates, 1):
        logger.info(f"   {i}. {candidate['filename']} - Score: {candidate['quality_score']:.1f}")
    
    return top_candidates

if __name__ == "__main__":
    # Utiliser votre dataset organisé par domaines
    dataset_path = "C:/Users/Me/Desktop/RH/dataset"
    
    # Vérifier que le dataset existe
    if not os.path.exists(dataset_path):
        logger.error(f"❌ Dataset non trouvé: {dataset_path}")
        logger.info("Veuillez vérifier le chemin du dataset")
    else:
        logger.info(f"📁 Dataset trouvé: {dataset_path}")
        
        # Compter les CV par domaine
        domain_counts = {}
        for domain_folder in os.listdir(dataset_path):
            domain_path = os.path.join(dataset_path, domain_folder)
            if os.path.isdir(domain_path):
                cv_count = len([f for f in os.listdir(domain_path) if f.endswith('.pdf')])
                domain_counts[domain_folder] = cv_count
        
        logger.info("📊 Aperçu du dataset:")
        total_cvs = sum(domain_counts.values())
        logger.info(f"   Total CVs: {total_cvs}")
        for domain, count in sorted(domain_counts.items()):
            logger.info(f"   {domain}: {count} CVs")
        
        # Entraîner les modèles avec votre dataset complet
        analyzer, cv_df = train_ai_models(dataset_path)
        
        if analyzer and not cv_df.empty:
            # Tester le filtrage sur les domaines principaux
            test_filtering(analyzer, cv_df, "INFORMATION-TECHNOLOGY", 10)
            test_filtering(analyzer, cv_df, "TEACHER", 5)
            test_filtering(analyzer, cv_df, "ADVOCATE", 5)
            test_filtering(analyzer, cv_df, "ACCOUNTANT", 5)
            test_filtering(analyzer, cv_df, "ENGINEERING", 5)
