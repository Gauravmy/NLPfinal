"""
Model Comparison Module

This module implements and compares different resume ranking strategies:
1. TF-IDF based ranking
2. Hybrid ranking (TF-IDF + Skill matching)
3. BERT-based ranking
4. Deep Ensemble ranking (combined approach)

Provides evaluation and comparison of these approaches using metrics like
Precision@K, Recall@K, and Mean Average Precision (MAP).
"""

import logging
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np

from src.similarity_model import (
    tfidf_similarity_bulk,
    bert_similarity_bulk,
    deep_ensemble_similarity_bulk
)
from src.skill_extractor import calculate_skill_match_percentage
from src.evaluation import (
    precision_at_k_multi,
    recall_at_k_multi,
    mean_average_precision_multi
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def rank_by_tfidf(df: pd.DataFrame, job_description: str,
                  score_column: str = 'tfidf_score') -> pd.DataFrame:
    """
    Rank resumes using TF-IDF similarity scores.
    
    Args:
        df (pd.DataFrame): DataFrame with 'resume_text' column
        job_description (str): Job description text
        score_column (str): Name of column to store scores
        
    Returns:
        pd.DataFrame: Ranked DataFrame with scores
    """
    try:
        logger.info("Computing TF-IDF rankings...")
        
        resume_texts = df['resume_text'].tolist()
        scores = tfidf_similarity_bulk(resume_texts, job_description)
        
        result_df = df.copy()
        result_df[score_column] = scores
        result_df = result_df.sort_values(by=score_column, ascending=False)
        
        logger.info(f"TF-IDF ranking complete. Top score: {scores.max():.4f}")
        return result_df
        
    except Exception as e:
        logger.error(f"Error in TF-IDF ranking: {e}")
        return df


def rank_by_bert(df: pd.DataFrame, job_description: str,
                 score_column: str = 'bert_score',
                 show_progress: bool = False) -> pd.DataFrame:
    """
    Rank resumes using BERT similarity scores.
    
    Args:
        df (pd.DataFrame): DataFrame with 'resume_text' column
        job_description (str): Job description text
        score_column (str): Name of column to store scores
        show_progress (bool): Whether to show progress bar
        
    Returns:
        pd.DataFrame: Ranked DataFrame with scores
    """
    try:
        logger.info("Computing BERT rankings...")
        
        resume_texts = df['resume_text'].tolist()
        scores = bert_similarity_bulk(resume_texts, job_description, 
                                     show_progress=show_progress)
        
        result_df = df.copy()
        result_df[score_column] = scores
        result_df = result_df.sort_values(by=score_column, ascending=False)
        
        logger.info(f"BERT ranking complete. Top score: {scores.max():.4f}")
        return result_df
        
    except Exception as e:
        logger.error(f"Error in BERT ranking: {e}")
        return df


def rank_by_hybrid(df: pd.DataFrame, job_description: str,
                  job_skills: set,
                  tfidf_weight: float = 0.7,
                  skill_weight: float = 0.3,
                  score_column: str = 'hybrid_score') -> pd.DataFrame:
    """
    Rank resumes using hybrid approach (TF-IDF + Skill matching).
    
    Args:
        df (pd.DataFrame): DataFrame with 'resume_text' and 'skills' columns
        job_description (str): Job description text
        job_skills (set): Set of required skills
        tfidf_weight (float): Weight for TF-IDF component
        skill_weight (float): Weight for skill component
        score_column (str): Name of column to store scores
        
    Returns:
        pd.DataFrame: Ranked DataFrame with scores
    """
    try:
        logger.info("Computing Hybrid rankings...")
        
        # Normalize weights
        total = tfidf_weight + skill_weight
        tfidf_weight = tfidf_weight / total
        skill_weight = skill_weight / total
        
        # Get TF-IDF scores
        resume_texts = df['resume_text'].tolist()
        tfidf_scores = tfidf_similarity_bulk(resume_texts, job_description)
        
        # Get skill match scores
        skill_scores = []
        for skills in df['skills']:
            score = calculate_skill_match_percentage(skills, job_skills) / 100.0
            skill_scores.append(score)
        
        # Compute hybrid score
        hybrid_scores = (
            tfidf_weight * tfidf_scores +
            skill_weight * np.array(skill_scores)
        )
        
        result_df = df.copy()
        result_df[score_column] = hybrid_scores
        result_df = result_df.sort_values(by=score_column, ascending=False)
        
        logger.info(f"Hybrid ranking complete. Top score: {hybrid_scores.max():.4f}")
        return result_df
        
    except Exception as e:
        logger.error(f"Error in Hybrid ranking: {e}")
        return df


def rank_by_deep_ensemble(df: pd.DataFrame, job_description: str,
                         job_skills: set,
                         tfidf_weight: float = 0.5,
                         bert_weight: float = 0.3,
                         skill_weight: float = 0.2,
                         score_column: str = 'deep_ensemble_score') -> pd.DataFrame:
    """
    Rank resumes using deep ensemble approach.
    Combines TF-IDF, BERT, and Skill matching with specified weights.
    
    Args:
        df (pd.DataFrame): DataFrame with resume and skill columns
        job_description (str): Job description text
        job_skills (set): Set of required skills
        tfidf_weight (float): Weight for TF-IDF (default: 0.5)
        bert_weight (float): Weight for BERT (default: 0.3)
        skill_weight (float): Weight for skill matching (default: 0.2)
        score_column (str): Name of column to store scores
        
    Returns:
        pd.DataFrame: Ranked DataFrame with scores
    """
    try:
        logger.info("Computing Deep Ensemble rankings...")
        
        # Normalize weights
        total = tfidf_weight + bert_weight + skill_weight
        tfidf_weight = tfidf_weight / total
        bert_weight = bert_weight / total
        skill_weight = skill_weight / total
        
        logger.info(f"Using weights - TF-IDF: {tfidf_weight:.2f}, "
                   f"BERT: {bert_weight:.2f}, Skills: {skill_weight:.2f}")
        
        # Get all component scores
        resume_texts = df['resume_text'].tolist()
        
        tfidf_scores = tfidf_similarity_bulk(resume_texts, job_description)
        bert_scores = bert_similarity_bulk(resume_texts, job_description, 
                                          show_progress=False)
        
        skill_scores = []
        for skills in df['skills']:
            score = calculate_skill_match_percentage(skills, job_skills) / 100.0
            skill_scores.append(score)
        skill_scores = np.array(skill_scores)
        
        # Compute deep ensemble score
        ensemble_scores = (
            tfidf_weight * tfidf_scores +
            bert_weight * bert_scores +
            skill_weight * skill_scores
        )
        
        result_df = df.copy()
        result_df[score_column] = ensemble_scores
        result_df = result_df.sort_values(by=score_column, ascending=False)
        
        logger.info(f"Deep Ensemble ranking complete. Top score: {ensemble_scores.max():.4f}")
        return result_df
        
    except Exception as e:
        logger.error(f"Error in Deep Ensemble ranking: {e}")
        return df


def compare_models(df: pd.DataFrame, job_description: str,
                  job_skills: set,
                  relevant_categories: List[str] = None,
                  k: int = 10) -> Dict[str, Dict[str, float]]:
    """
    Compare performance of all ranking models on the dataset.
    
    Args:
        df (pd.DataFrame): DataFrame with resume data including 'category' column
        job_description (str): Job description text
        job_skills (set): Set of required skills
        relevant_categories (List[str]): Categories to consider as relevant
        k (int): K value for Precision@K and Recall@K metrics
        
    Returns:
        Dict[str, Dict[str, float]]: Comparison results with metrics for each model
    """
    try:
        if not relevant_categories:
            relevant_categories = list(df['category'].unique())[:2]
        
        logger.info(f"Comparing models across {len(relevant_categories)} "
                   f"relevant categories: {relevant_categories}")
        
        # Generate rankings from each model
        tfidf_ranked = rank_by_tfidf(df, job_description)
        bert_ranked = rank_by_bert(df, job_description)
        hybrid_ranked = rank_by_hybrid(df, job_description, job_skills)
        deep_ranked = rank_by_deep_ensemble(df, job_description, job_skills)
        
        # Evaluate each model
        results = {}
        
        models = {
            'TF-IDF': tfidf_ranked,
            'BERT': bert_ranked,
            'Hybrid': hybrid_ranked,
            'Deep Ensemble': deep_ranked
        }
        
        for model_name, ranked_df in models.items():
            logger.info(f"Evaluating {model_name}...")
            
            metrics = {
                'Precision@10': precision_at_k_multi(
                    ranked_df, k, 'category', relevant_categories
                ),
                'Recall@10': recall_at_k_multi(
                    ranked_df, k, 'category', relevant_categories
                ),
                'MAP': mean_average_precision_multi(
                    ranked_df, 'category', relevant_categories
                )
            }
            
            results[model_name] = metrics
        
        logger.info(f"Model comparison complete: {results}")
        return results
        
    except Exception as e:
        logger.error(f"Error in model comparison: {e}")
        return {}


def comparison_to_dataframe(comparison_results: Dict[str, Dict[str, float]]) -> pd.DataFrame:
    """
    Convert comparison results to a pandas DataFrame for easy viewing and analysis.
    
    Args:
        comparison_results (Dict): Dictionary of model comparison results
        
    Returns:
        pd.DataFrame: Comparison results as DataFrame
    """
    try:
        if not comparison_results:
            logger.warning("Empty comparison results provided")
            return pd.DataFrame()
        
        df_comparison = pd.DataFrame(comparison_results).T
        df_comparison = df_comparison.round(4)
        
        logger.info("Comparison DataFrame created:\n" + str(df_comparison))
        return df_comparison
        
    except Exception as e:
        logger.error(f"Error converting comparison to DataFrame: {e}")
        return pd.DataFrame()


def save_comparison_results(comparison_df: pd.DataFrame, 
                           output_path: str = "model_comparison_results.csv") -> bool:
    """
    Save model comparison results to CSV file.
    
    Args:
        comparison_df (pd.DataFrame): Comparison results DataFrame
        output_path (str): Path to save the CSV file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        comparison_df.to_csv(output_path)
        logger.info(f"Comparison results saved to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving comparison results: {e}")
        return False
