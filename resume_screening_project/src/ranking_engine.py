"""
Ranking Engine Module

This module ranks candidates based on combined scoring:
- Similarity Score: 70% weight
- Skill Match Percentage: 30% weight
"""

import logging
from typing import List, Dict, Tuple
from src.similarity_model import compute_similarity
from src.skill_extractor import calculate_skill_match_percentage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def rank_candidates(candidate_resumes: Dict[str, Tuple[str, set]], 
                   job_description: str,
                   job_skills: set,
                   similarity_weight: float = 0.7,
                   skill_weight: float = 0.3) -> List[Dict]:
    """
    Rank candidates based on similarity and skill matching.
    
    Scoring Formula:
    Final Score = (Similarity Score * 0.7) + (Skill Match % / 100 * 0.3)
    
    Args:
        candidate_resumes (Dict): Dictionary with candidate names as keys and
                                 tuples of (resume_text, extracted_skills)
        job_description (str): Job description text
        job_skills (set): Set of skills required for the job
        similarity_weight (float): Weight for similarity score (default 0.7)
        skill_weight (float): Weight for skill match (default 0.3)
        
    Returns:
        List[Dict]: Ranked candidates with scores and rankings
    """
    try:
        if not candidate_resumes:
            logger.warning("No candidate resumes provided")
            return []
        
        epsilon = 1e-9
        if abs(similarity_weight + skill_weight - 1.0) > epsilon:
            logger.warning("Weights don't sum to 1.0, normalizing...")
            total = similarity_weight + skill_weight
            similarity_weight /= total
            skill_weight /= total
        
        candidate_scores = []
        
        for candidate_name, (resume_text, resume_skills) in candidate_resumes.items():
            try:
                # Calculate similarity score
                similarity_score, _ = compute_similarity(resume_text, job_description)
                
                # Calculate skill match percentage
                skill_match_pct = calculate_skill_match_percentage(job_skills, resume_skills)
                skill_match_normalized = skill_match_pct / 100
                
                # Calculate final score
                final_score = (similarity_score * similarity_weight) + \
                             (skill_match_normalized * skill_weight)
                
                candidate_scores.append({
                    'candidate_name': candidate_name,
                    'similarity_score': round(similarity_score * 100, 2),  # Convert to 0-100
                    'skill_match_percentage': skill_match_pct,
                    'final_score': round(final_score * 100, 2),  # Convert to 0-100
                    'extracted_skills': resume_skills,
                    'matching_skills': job_skills & resume_skills,
                    'missing_skills': job_skills - resume_skills
                })
                
                logger.info(f"Scored candidate: {candidate_name} - "
                          f"Similarity: {similarity_score:.4f}, "
                          f"Skill Match: {skill_match_pct:.2f}%")
                
            except Exception as e:
                logger.warning(f"Error scoring candidate {candidate_name}: {e}")
                continue
        
        # Sort by final score in descending order
        ranked_candidates = sorted(candidate_scores, 
                                  key=lambda x: x['final_score'], 
                                  reverse=True)
        
        # Add ranking number
        for idx, candidate in enumerate(ranked_candidates, 1):
            candidate['rank'] = idx
        
        logger.info(f"Ranking complete. Top candidate: "
                   f"{ranked_candidates[0]['candidate_name'] if ranked_candidates else 'None'}")
        
        return ranked_candidates
        
    except Exception as e:
        logger.error(f"Error during candidate ranking: {e}")
        raise


def get_top_candidates(ranked_candidates: List[Dict], top_n: int = 5) -> List[Dict]:
    """
    Get top N candidates from ranking results.
    
    Args:
        ranked_candidates (List[Dict]): Ranked candidate list
        top_n (int): Number of top candidates to return
        
    Returns:
        List[Dict]: Top N candidates
    """
    return ranked_candidates[:top_n]


def get_candidate_summary(ranked_candidates: List[Dict]) -> Dict:
    """
    Get summary statistics of candidate ranking.
    
    Args:
        ranked_candidates (List[Dict]): Ranked candidate list
        
    Returns:
        Dict: Summary statistics
    """
    if not ranked_candidates:
        return {
            'total_candidates': 0,
            'average_score': 0.0,
            'max_score': 0.0,
            'min_score': 0.0,
            'top_candidate': None
        }
    
    scores = [c['final_score'] for c in ranked_candidates]
    
    return {
        'total_candidates': len(ranked_candidates),
        'average_score': round(sum(scores) / len(scores), 2),
        'max_score': max(scores),
        'min_score': min(scores),
        'top_candidate': ranked_candidates[0]['candidate_name'],
        'top_candidate_score': ranked_candidates[0]['final_score']
    }


def filter_candidates_by_threshold(ranked_candidates: List[Dict], 
                                   threshold: float = 60.0) -> List[Dict]:
    """
    Filter candidates by minimum score threshold.
    
    Args:
        ranked_candidates (List[Dict]): Ranked candidate list
        threshold (float): Minimum score to qualify (0-100)
        
    Returns:
        List[Dict]: Candidates meeting threshold
    """
    if not isinstance(threshold, (int, float)) or threshold < 0 or threshold > 100:
        logger.warning(f"Invalid threshold {threshold}, using default 60")
        threshold = 60.0
    
    qualified = [c for c in ranked_candidates if c['final_score'] >= threshold]
    
    logger.info(f"Filtered {len(qualified)} candidates above threshold {threshold}")
    return qualified


def export_rankings_to_dict(ranked_candidates: List[Dict]) -> List[Dict]:
    """
    Convert rankings to exportable format.
    
    Args:
        ranked_candidates (List[Dict]): Ranked candidate list
        
    Returns:
        List[Dict]: Exportable format
    """
    export_data = []
    
    for candidate in ranked_candidates:
        export_data.append({
            'Rank': candidate['rank'],
            'Candidate': candidate['candidate_name'],
            'Final Score': candidate['final_score'],
            'Similarity Score': candidate['similarity_score'],
            'Skill Match %': candidate['skill_match_percentage'],
            'Matched Skills': ', '.join(candidate['matching_skills']) if candidate['matching_skills'] else 'None',
            'Missing Skills': ', '.join(candidate['missing_skills']) if candidate['missing_skills'] else 'None',
            'Total Skills': len(candidate['extracted_skills'])
        })
    
    return export_data


# ============================================================================
# Ensemble-based Ranking Functions for DataFrame Operations
# ============================================================================

def rank_by_bert_similarity(candidate_resumes: Dict[str, Tuple[str, set]],
                           job_description: str,
                           job_skills: set) -> List[Dict]:
    """
    Rank candidates using BERT similarity score.
    
    Args:
        candidate_resumes (Dict): Dictionary with candidate names and resume data
        job_description (str): Job description text
        job_skills (set): Set of required skills
        
    Returns:
        List[Dict]: Ranked candidates with BERT scores
    """
    try:
        from src.similarity_model import bert_similarity
        
        if not candidate_resumes:
            logger.warning("No candidate resumes provided")
            return []
        
        candidate_scores = []
        
        for candidate_name, (resume_text, resume_skills) in candidate_resumes.items():
            try:
                # Calculate BERT similarity
                bert_score = bert_similarity(resume_text, job_description)
                
                candidate_scores.append({
                    'candidate_name': candidate_name,
                    'bert_score': round(bert_score * 100, 2),
                    'extracted_skills': resume_skills,
                    'matching_skills': job_skills & resume_skills
                })
                
                logger.debug(f"BERT scored candidate: {candidate_name} - {bert_score:.4f}")
                
            except Exception as e:
                logger.warning(f"Error scoring candidate {candidate_name} with BERT: {e}")
                continue
        
        # Sort by BERT score
        ranked_candidates = sorted(candidate_scores,
                                  key=lambda x: x['bert_score'],
                                  reverse=True)
        
        for idx, candidate in enumerate(ranked_candidates, 1):
            candidate['rank'] = idx
        
        logger.info(f"BERT ranking complete. Top {len(ranked_candidates)} candidates scored")
        return ranked_candidates
        
    except Exception as e:
        logger.error(f"Error during BERT ranking: {e}")
        return []


def rank_by_ensemble(candidate_resumes: Dict[str, Tuple[str, set]],
                    job_description: str,
                    job_skills: set,
                    tfidf_weight: float = 0.5,
                    bert_weight: float = 0.3,
                    skill_weight: float = 0.2) -> List[Dict]:
    """
    Rank candidates using deep ensemble approach combining TF-IDF, BERT, and skills.
    
    Args:
        candidate_resumes (Dict): Dictionary with candidate names and resume data
        job_description (str): Job description text
        job_skills (set): Set of required skills
        tfidf_weight (float): Weight for TF-IDF (default: 0.5)
        bert_weight (float): Weight for BERT (default: 0.3)
        skill_weight (float): Weight for skill matching (default: 0.2)
        
    Returns:
        List[Dict]: Ranked candidates with ensemble scores
    """
    try:
        from src.similarity_model import tfidf_similarity, bert_similarity
        
        if not candidate_resumes:
            logger.warning("No candidate resumes provided")
            return []
        
        # Normalize weights
        total = tfidf_weight + bert_weight + skill_weight
        tfidf_weight = tfidf_weight / total
        bert_weight = bert_weight / total
        skill_weight = skill_weight / total
        
        logger.info(f"Ensemble weights - TF-IDF: {tfidf_weight:.2f}, "
                   f"BERT: {bert_weight:.2f}, Skills: {skill_weight:.2f}")
        
        candidate_scores = []
        
        for candidate_name, (resume_text, resume_skills) in candidate_resumes.items():
            try:
                # Calculate all components
                tfidf_score = tfidf_similarity(resume_text, job_description)
                bert_score = bert_similarity(resume_text, job_description)
                
                skill_match_pct = calculate_skill_match_percentage(job_skills, resume_skills)
                skill_match_norm = skill_match_pct / 100.0
                
                # Compute ensemble score
                ensemble_score = (
                    tfidf_weight * tfidf_score +
                    bert_weight * bert_score +
                    skill_weight * skill_match_norm
                )
                
                candidate_scores.append({
                    'candidate_name': candidate_name,
                    'tfidf_score': round(tfidf_score * 100, 2),
                    'bert_score': round(bert_score * 100, 2),
                    'skill_match_percentage': skill_match_pct,
                    'ensemble_score': round(ensemble_score * 100, 2),
                    'extracted_skills': resume_skills,
                    'matching_skills': job_skills & resume_skills,
                    'missing_skills': job_skills - resume_skills
                })
                
                logger.debug(f"Ensemble scored {candidate_name}: "
                           f"TF-IDF={tfidf_score:.4f}, BERT={bert_score:.4f}, "
                           f"Ensemble={ensemble_score:.4f}")
                
            except Exception as e:
                logger.warning(f"Error scoring candidate {candidate_name}: {e}")
                continue
        
        # Sort by ensemble score
        ranked_candidates = sorted(candidate_scores,
                                  key=lambda x: x['ensemble_score'],
                                  reverse=True)
        
        for idx, candidate in enumerate(ranked_candidates, 1):
            candidate['rank'] = idx
        
        logger.info(f"Ensemble ranking complete. Top candidate: "
                   f"{ranked_candidates[0]['candidate_name'] if ranked_candidates else 'None'}")
        return ranked_candidates
        
    except Exception as e:
        logger.error(f"Error during ensemble ranking: {e}")
        raise
