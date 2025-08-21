from django.shortcuts import render

"""
API Views pour l'analyse IA des CV
Endpoints pour upload et filtrage automatique des CV
"""
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import tempfile
from .cv_processor import CVAnalyzer
import logging

logger = logging.getLogger(__name__)

# Instance globale de l'analyseur
analyzer = CVAnalyzer()

# Charger les modèles pré-entraînés au démarrage
try:
    models_path = "C:/Users/Me/Desktop/RH/ai-model"
    if os.path.exists(models_path):
        analyzer.load_models(models_path)
        logger.info("✅ Modèles IA chargés avec succès")
    else:
        logger.warning("⚠️ Modèles IA non trouvés, utilisez l'entraînement d'abord")
except Exception as e:
    logger.error(f"❌ Erreur lors du chargement des modèles: {e}")

@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser])
def upload_and_analyze_cv(request):
    """
    Upload et analyse d'un CV individuel
    """
    try:
        if 'cv_file' not in request.FILES:
            return Response({
                'status': 'error',
                'filename': 'N/A',
                'error': 'Aucun fichier CV fourni',
                'message': 'Veuillez sélectionner un fichier CV à analyser'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        cv_file = request.FILES['cv_file']
        
        # Vérifier le format du fichier
        allowed_extensions = ['.pdf', '.docx', '.doc', '.txt']
        file_extension = os.path.splitext(cv_file.name)[1].lower()
        
        if file_extension not in allowed_extensions:
            return Response({
                'status': 'error',
                'filename': cv_file.name,
                'error': f'Format de fichier non supporté',
                'message': f'Formats acceptés: {", ".join(allowed_extensions)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Sauvegarder temporairement le fichier
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            for chunk in cv_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        try:
            # Extraire le texte du CV
            text = analyzer.processor.extract_text(temp_file_path)
            
            if not text:
                return Response({
                    'status': 'error',
                    'filename': cv_file.name,
                    'error': 'Impossible d\'extraire le texte du CV',
                    'message': 'Le fichier semble être vide ou corrompu'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Analyser le CV avec l'IA
            if analyzer.is_trained:
                analysis = analyzer.analyze_cv(text)
                
                return Response({
                    'status': 'success',
                    'filename': cv_file.name,
                    'domain': analysis['domain'],
                    'confidence': analysis['domain_confidence'],
                    'quality_score': analysis['quality_score'],
                    'skills': analysis['skills'],
                    'skills_count': analysis['skills_count'],
                    'experience_years': analysis['experience_years'],
                    'word_count': analysis['word_count'],
                    'text_preview': text[:500] + '...' if len(text) > 500 else text
                })
            else:
                return Response({
                    'status': 'error',
                    'filename': cv_file.name,
                    'error': 'L\'IA n\'est pas encore entraînée. Veuillez entraîner les modèles d\'abord.',
                    'message': 'Les modèles d\'IA doivent être entraînés avant l\'analyse'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                
        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse du CV: {e}")
        return Response({
            'status': 'error',
            'filename': getattr(cv_file, 'name', 'N/A') if 'cv_file' in locals() else 'N/A',
            'error': f'Erreur lors de l\'analyse',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def bulk_cv_analysis(request):
    """
    Analyse en lot de plusieurs CV et filtrage par domaine
    """
    try:
        if not analyzer.is_trained:
            return Response({
                'error': 'L\'IA n\'est pas encore entraînée.'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Récupérer les paramètres
        domain = request.data.get('domain', 'information_technology')
        top_n = int(request.data.get('top_n', 10))
        
        if 'cv_files' not in request.FILES:
            return Response({
                'error': 'Aucun fichier CV fourni'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        cv_files = request.FILES.getlist('cv_files')
        
        if len(cv_files) == 0:
            return Response({
                'error': 'Liste de fichiers vide'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        analyses = []
        
        for cv_file in cv_files:
            try:
                # Vérifier le format
                file_extension = os.path.splitext(cv_file.name)[1].lower()
                if file_extension not in ['.pdf', '.docx', '.doc', '.txt']:
                    continue
                
                # Traiter le fichier
                with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                    for chunk in cv_file.chunks():
                        temp_file.write(chunk)
                    temp_file_path = temp_file.name
                
                try:
                    text = analyzer.processor.extract_text(temp_file_path)
                    if text:
                        analysis = analyzer.analyze_cv(text)
                        analysis['filename'] = cv_file.name
                        analyses.append(analysis)
                finally:
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                        
            except Exception as e:
                logger.error(f"Erreur avec le fichier {cv_file.name}: {e}")
                continue
        
        if not analyses:
            return Response({
                'error': 'Aucun CV n\'a pu être analysé'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Organiser les résultats par domaine
        domain_summary = {}
        for analysis in analyses:
            domain_name = analysis['domain']
            if domain_name not in domain_summary:
                domain_summary[domain_name] = {
                    'count': 0,
                    'top_candidates': []
                }
            domain_summary[domain_name]['count'] += 1
            
            # Ajouter le candidat avec le format attendu par le frontend
            candidate = {
                'status': 'success',
                'filename': analysis['filename'],
                'domain': analysis['domain'],
                'confidence': analysis['domain_confidence'],
                'quality_score': analysis['quality_score'],
                'skills': analysis['skills'],
                'experience_years': analysis['experience_years']
            }
            domain_summary[domain_name]['top_candidates'].append(candidate)
        
        # Trier les candidats par score de qualité pour chaque domaine
        for domain_name in domain_summary:
            domain_summary[domain_name]['top_candidates'].sort(
                key=lambda x: x['quality_score'], 
                reverse=True
            )
            # Garder seulement les top 10
            domain_summary[domain_name]['top_candidates'] = domain_summary[domain_name]['top_candidates'][:10]
        
        return Response({
            'status': 'success',
            'total_files': len(cv_files),
            'processed_files': len(analyses),
            'results': [
                {
                    'status': 'success',
                    'filename': analysis['filename'],
                    'domain': analysis['domain'],
                    'confidence': analysis['domain_confidence'],
                    'quality_score': analysis['quality_score'],
                    'skills': analysis['skills'],
                    'experience_years': analysis['experience_years']
                } for analysis in analyses
            ],
            'summary': domain_summary
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse en lot: {e}")
        return Response({
            'error': f'Erreur lors de l\'analyse: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def ai_status(request):
    """
    Statut de l'IA et domaines disponibles
    """
    try:
        domains_available = [
            'information_technology', 'teacher', 'advocate', 'accountant',
            'engineering', 'healthcare', 'finance', 'banking', 'sales',
            'marketing', 'hr', 'consultant', 'designer', 'chef'
        ]
        
        return Response({
            'ai_trained': analyzer.is_trained,
            'available_domains': domains_available,
            'supported_formats': ['.pdf', '.docx', '.doc', '.txt'],
            'status': 'IA opérationnelle' if analyzer.is_trained else 'IA non entraînée'
        })
        
    except Exception as e:
        return Response({
            'error': f'Erreur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def analyze_job_cvs(request):
    """
    Analyse de CV spécifiquement pour un poste donné
    """
    try:
        if not analyzer.is_trained:
            return Response({
                'error': 'L\'IA n\'est pas encore entraînée.'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Récupérer les informations du poste
        job_id = request.data.get('job_id')
        job_title = request.data.get('job_title', '')
        job_description = request.data.get('job_description', '')
        job_requirements = request.data.get('job_requirements', '')
        required_skills = request.data.get('required_skills', '')
        experience_required = request.data.get('experience_required', '')
        
        if 'files' not in request.FILES:
            return Response({
                'error': 'Aucun fichier CV fourni'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        cv_files = request.FILES.getlist('files')
        
        if len(cv_files) == 0:
            return Response({
                'error': 'Liste de fichiers vide'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        analyses = []
        skills_keywords = [skill.strip().lower() for skill in required_skills.split(',') if skill.strip()]
        
        for cv_file in cv_files:
            try:
                # Vérifier le format
                file_extension = os.path.splitext(cv_file.name)[1].lower()
                if file_extension not in ['.pdf', '.docx', '.doc', '.txt']:
                    continue

                # Traiter le fichier
                with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                    for chunk in cv_file.chunks():
                        temp_file.write(chunk)
                    temp_file_path = temp_file.name

                try:
                    text = analyzer.processor.extract_text(temp_file_path)
                    if text:
                        # Analyse de base du CV
                        analysis = analyzer.analyze_cv(text)
                        analysis['filename'] = cv_file.name

                        # Calcul du score de correspondance avec le poste
                        candidate_experience = analysis.get('experience_years', 0)
                        required_min, required_max = parse_experience_range(experience_required)
                        # Strict filter: only include CVs whose experience is within the required range
                        if required_max >= 10:
                            # For '10+', only include CVs with 10 years or more
                            if candidate_experience < 10:
                                continue
                        else:
                            # For ranges, only include CVs within [min, max]
                            if candidate_experience < required_min or candidate_experience > required_max:
                                continue

                        job_match_score = calculate_job_match_score(
                            text.lower(), 
                            skills_keywords, 
                            job_description.lower(),
                            job_requirements.lower(),
                            experience_required,
                            candidate_experience
                        )
                        analysis['job_match_score'] = job_match_score

                        analyses.append(analysis)
                finally:
                    # Nettoyer le fichier temporaire
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)

            except Exception as e:
                logger.error(f"Erreur lors de l'analyse de {cv_file.name}: {e}")
                continue

        # Trier les candidats par score de correspondance
        ranked_candidates = sorted(analyses, key=lambda x: x.get('job_match_score', 0), reverse=True)

        return Response({
            'total_files': len(cv_files),
            'processed_files': len(analyses),
            'job_info': {
                'title': job_title,
                'company': request.data.get('company_name', ''),
                'required_skills': skills_keywords
            },
            'results': analyses,
            'ranked_candidates': ranked_candidates[:10]  # Top 10 candidats
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse des CV pour le poste: {e}")
        return Response({
            'error': f'Erreur lors de l\'analyse: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def calculate_job_match_score(cv_text, required_skills, job_description, job_requirements, experience_required, candidate_experience):
    """
    Calcule un score de correspondance entre un CV et un poste
    """
    total_score = 0
    
    # 1. Score basé sur les compétences requises (50% du score total)
    skills_score = 0
    if required_skills:
        found_skills = 0
        for skill in required_skills:
            if skill in cv_text:
                found_skills += 1
        skills_score = (found_skills / len(required_skills)) * 50 if required_skills else 0
    
    # 2. Score basé sur l'expérience (30% du score total)
    experience_score = calculate_experience_match(experience_required, candidate_experience)
    
    # 3. Score basé sur les mots-clés de la description (20% du score total)
    description_keywords = ['python', 'java', 'javascript', 'react', 'django', 'machine learning', 
                          'data', 'sql', 'git', 'agile', 'scrum', 'docker', 'kubernetes', 'api',
                          'frontend', 'backend', 'database', 'cloud', 'aws', 'azure']
    description_score = 0
    found_keywords = 0
    combined_text = f"{cv_text} {job_description} {job_requirements}"
    for keyword in description_keywords:
        if keyword in combined_text:
            found_keywords += 1
    description_score = min((found_keywords / len(description_keywords)) * 20, 20)
    
    total_score = skills_score + experience_score + description_score
    return min(total_score, 100)


def calculate_experience_match(experience_required, candidate_experience):
    """
    Calcule le score de correspondance d'expérience (sur 30 points)
    """
    if not experience_required:
        return 30  # Si pas d'exigence, score maximum

    # Parser l'expérience requise
    required_min, required_max = parse_experience_range(experience_required)

    # Hard filter: if candidate experience is below required minimum, score is 0 (except for entry-level)
    if required_min >= 1 and candidate_experience < required_min:
        return 0

    # Si le candidat n'a pas d'expérience et que c'est requis
    if candidate_experience == 0 and required_min > 0:
        return 0

    # Si le candidat a l'expérience exacte requise
    if required_min <= candidate_experience <= required_max:
        return 30  # Score maximum

    # Si le candidat a plus d'expérience que requis (sur-qualification)
    if candidate_experience > required_max:
        # Légère pénalité pour sur-qualification
        excess = candidate_experience - required_max
        penalty = min(excess * 2, 10)  # Maximum 10 points de pénalité
        return max(30 - penalty, 20)

    return 15  # Score moyen par défaut


def parse_experience_range(experience_str):
    """
    Parse une string d'expérience comme '1-3' ou '5-10' ou '10+'
    Retourne (min_years, max_years)
    """
    experience_str = experience_str.lower().strip()
    
    if '+' in experience_str:
        # Format '10+'
        min_years = int(experience_str.replace('+', ''))
        max_years = min_years + 10  # Assume max 10 ans de plus
        return min_years, max_years
    
    if '-' in experience_str:
        # Format '1-3'
        parts = experience_str.split('-')
        if len(parts) == 2:
            try:
                min_years = int(parts[0])
                max_years = int(parts[1])
                return min_years, max_years
            except ValueError:
                pass
    
    # Format '0' ou autre
    try:
        years = int(experience_str)
        return years, years
    except ValueError:
        return 0, 0  # Défaut si impossible à parser
