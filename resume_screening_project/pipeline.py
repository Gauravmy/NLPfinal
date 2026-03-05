"""
End-to-End Resume Screening Pipeline

This script implements a complete resume screening pipeline integrating the Kaggle code:
1. PDF extraction from resume directory
2. Text preprocessing and cleaning
3. Skill extraction using NLP
4. Multiple ranking approaches (TF-IDF, BERT, Hybrid, Deep Ensemble)
5. Model evaluation and comparison
6. Results visualization and export

Usage:
    python pipeline.py --data_path ./data/resumes --job_desc "job_description.txt" --output ./results
"""

import os
import sys
import argparse
import logging
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import joblib

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.resume_parser import parse_resume
from src.text_preprocessing import preprocess_text
from src.skill_extractor import extract_skills, SKILL_DICTIONARY
from src.similarity_model import (
    tfidf_similarity_bulk,
    bert_similarity_bulk,
    deep_ensemble_similarity_bulk,
    initialize_bert_model
)
from src.skill_extractor import extract_job_skills
from src.data_integrator import DataIntegrator, quick_integrate_data
from src.model_comparison import (
    rank_by_tfidf,
    rank_by_bert,
    rank_by_hybrid,
    rank_by_deep_ensemble,
    compare_models,
    comparison_to_dataframe,
    save_comparison_results
)
from src.evaluation import (
    precision_at_k_multi,
    recall_at_k_multi,
    mean_average_precision_multi
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_resumes_from_directory(data_path: str) -> pd.DataFrame:
    """
    Load all PDF resumes from directory structure.
    
    Expected structure:
    data_path/
        category1/
            resume1.pdf
            resume2.pdf
        category2/
            resume3.pdf
    
    Args:
        data_path (str): Path to data directory
        
    Returns:
        pd.DataFrame: DataFrame with resume data
    """
    logger.info(f"Loading resumes from {data_path}...")
    
    data = []
    
    for category in tqdm(os.listdir(data_path)):
        category_path = os.path.join(data_path, category)
        
        if os.path.isdir(category_path):
            logger.info(f"Processing category: {category}")
            
            for file in tqdm(os.listdir(category_path)):
                if file.endswith(".pdf"):
                    try:
                        pdf_path = os.path.join(category_path, file)
                        resume_text = parse_resume(pdf_path)
                        
                        data.append({
                            'filename': file,
                            'category': category,
                            'resume_text': resume_text,
                            'file_path': pdf_path
                        })
                        
                    except Exception as e:
                        logger.warning(f"Error processing {file}: {e}")
                        continue
                
                elif file.endswith(".txt"):
                    # Support text files from integrated CSV data
                    try:
                        txt_path = os.path.join(category_path, file)
                        with open(txt_path, 'r', encoding='utf-8') as f:
                            resume_text = f.read()
                        
                        data.append({
                            'filename': file,
                            'category': category,
                            'resume_text': resume_text,
                            'file_path': txt_path
                        })
                        
                    except Exception as e:
                        logger.warning(f"Error processing {file}: {e}")
                        continue
    
    df = pd.DataFrame(data)
    logger.info(f"Loaded {len(df)} resumes from {len(df['category'].unique())} categories")
    
    return df


def preprocess_resumes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess and clean resume texts.
    
    Args:
        df (pd.DataFrame): DataFrame with resume data
        
    Returns:
        pd.DataFrame: DataFrame with cleaned text
    """
    logger.info("Preprocessing resume texts...")
    
    df_copy = df.copy()
    df_copy['cleaned_text'] = df_copy['resume_text'].apply(preprocess_text)
    
    logger.info("Preprocessing complete")
    return df_copy


def extract_skills_from_resumes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract skills from all resumes.
    
    Args:
        df (pd.DataFrame): DataFrame with resume data
        
    Returns:
        pd.DataFrame: DataFrame with extracted skills
    """
    logger.info("Extracting skills from resumes...")
    
    df_copy = df.copy()
    df_copy['skills'] = df_copy['cleaned_text'].apply(
        lambda x: extract_skills(x)
    )
    
    logger.info(f"Skill extraction complete. Average skills per resume: "
               f"{df_copy['skills'].apply(len).mean():.1f}")
    
    return df_copy


def load_job_description(job_desc_path: str) -> str:
    """
    Load job description from file.
    
    Args:
        job_desc_path (str): Path to job description file
        
    Returns:
        str: Job description text
    """
    logger.info(f"Loading job description from {job_desc_path}...")
    
    try:
        with open(job_desc_path, 'r', encoding='utf-8') as f:
            job_description = f.read()
        
        logger.info(f"Job description loaded ({len(job_description)} characters)")
        return job_description
        
    except Exception as e:
        logger.error(f"Error loading job description: {e}")
        raise


def prepare_data(data_path: str, job_desc_path: str) -> tuple:
    """
    Complete data preparation pipeline.
    
    Args:
        data_path (str): Path to resume data directory
        job_desc_path (str): Path to job description file
        
    Returns:
        tuple: (DataFrame with processed resumes, job description, job skills)
    """
    # Load resumes
    df = load_resumes_from_directory(data_path)
    
    # Preprocess
    df = preprocess_resumes(df)
    
    # Extract skills
    df = extract_skills_from_resumes(df)
    
    # Load job description
    job_description = load_job_description(job_desc_path)
    clean_job_desc = preprocess_text(job_description)
    job_skills = extract_job_skills(job_description)
    
    logger.info(f"Job requires {len(job_skills)} skills")
    
    return df, clean_job_desc, job_skills


def integrate_csv_data(csv_path: str, data_path: str) -> bool:
    """
    Integrate resume data from CSV file into project directory.
    
    This function:
    1. Loads Resume.csv
    2. Organizes resumes by category
    3. Saves as text files in the project directory
    
    Args:
        csv_path (str): Path to Resume.csv file
        data_path (str): Target data directory
        
    Returns:
        bool: Success status
    """
    try:
        logger.info("\n" + "="*70)
        logger.info("INTEGRATING CSV RESUME DATA")
        logger.info("="*70)
        
        if not os.path.exists(csv_path):
            logger.error(f"CSV file not found: {csv_path}")
            return False
        
        os.makedirs(data_path, exist_ok=True)
        
        count, stats = quick_integrate_data(csv_path, data_path)
        
        if count > 0:
            logger.info(f"\n✓ Successfully integrated {count} resumes!")
            logger.info(f"Categories: {stats.get('categories', 0)}")
            logger.info(f"Category Distribution:")
            for category, cnt in stats.get('category_distribution', {}).items():
                logger.info(f"  • {category}: {cnt} resumes")
            logger.info("="*70 + "\n")
            return True
        else:
            logger.error("Failed to integrate CSV data")
            return False
            
    except Exception as e:
        logger.error(f"Error integrating CSV data: {e}", exc_info=True)
        return False


def run_ranking_pipeline(df: pd.DataFrame, job_description: str,
                        job_skills: set) -> dict:
    """
    Run all ranking algorithms.
    
    Args:
        df (pd.DataFrame): DataFrame with resume data
        job_description (str): Job description text
        job_skills (set): Set of required skills
        
    Returns:
        dict: Dictionary with rankings from each model
    """
    logger.info("Running ranking algorithms...")
    
    rankings = {}
    
    try:
        logger.info("1/4 Computing TF-IDF rankings...")
        rankings['TF-IDF'] = rank_by_tfidf(df, job_description)
        
        logger.info("2/4 Computing BERT rankings...")
        rankings['BERT'] = rank_by_bert(df, job_description, show_progress=False)
        
        logger.info("3/4 Computing Hybrid rankings...")
        rankings['Hybrid'] = rank_by_hybrid(df, job_description, job_skills)
        
        logger.info("4/4 Computing Deep Ensemble rankings...")
        rankings['Deep Ensemble'] = rank_by_deep_ensemble(
            df, job_description, job_skills,
            tfidf_weight=0.5,
            bert_weight=0.3,
            skill_weight=0.2
        )
        
        logger.info("Ranking pipeline complete")
        return rankings
        
    except Exception as e:
        logger.error(f"Error in ranking pipeline: {e}")
        raise


def evaluate_rankings(rankings: dict, relevant_categories: list,
                     k: int = 10) -> pd.DataFrame:
    """
    Evaluate all ranking models.
    
    Args:
        rankings (dict): Dictionary with rankings from each model
        relevant_categories (list): Categories considered relevant
        k (int): K value for Precision@K and Recall@K
        
    Returns:
        pd.DataFrame: Evaluation results
    """
    logger.info(f"Evaluating rankings against {len(relevant_categories)} "
               f"relevant categories...")
    
    results = {}
    
    for model_name, ranked_df in rankings.items():
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
    
    comparison_df = pd.DataFrame(results).T
    logger.info(f"\nModel Comparison Results:\n{comparison_df}")
    
    return comparison_df


def visualize_results(comparison_df: pd.DataFrame,
                     rankings: dict,
                     output_dir: str) -> None:
    """
    Create visualizations of results.
    
    Args:
        comparison_df (pd.DataFrame): Model comparison results
        rankings (dict): Ranking results from each model
        output_dir (str): Directory to save visualizations
    """
    logger.info("Creating visualizations...")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Model comparison bar chart
    plt.figure(figsize=(10, 6))
    comparison_df.plot(kind='bar', figsize=(10, 6))
    plt.title('Model Comparison: Resume Screening Performance')
    plt.ylabel('Metric Value')
    plt.xlabel('Model')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'model_comparison.png'), dpi=300)
    logger.info("Saved visualization: model_comparison.png")
    plt.close()
    
    # Top candidates comparison
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    for idx, (model_name, ranked_df) in enumerate(rankings.items()):
        ax = axes[idx // 2, idx % 2]
        
        top_10 = ranked_df.head(10)
        
        # Get the score column name for this model
        if 'tfidf_score' in top_10.columns:
            score_col = 'tfidf_score'
        elif 'bert_score' in top_10.columns:
            score_col = 'bert_score'
        elif 'hybrid_score' in top_10.columns:
            score_col = 'hybrid_score'
        elif 'deep_ensemble_score' in top_10.columns:
            score_col = 'deep_ensemble_score'
        else:
            score_col = top_10.columns[-1]
        
        ax.barh(range(len(top_10)), top_10[score_col].values)
        ax.set_yticks(range(len(top_10)))
        ax.set_yticklabels([f.replace('.pdf', '')[:20] for f in top_10['filename']], fontsize=8)
        ax.set_xlabel('Score')
        ax.set_title(f'{model_name} - Top 10 Resumes')
        ax.invert_yaxis()
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'top_candidates_comparison.png'), dpi=300)
    logger.info("Saved visualization: top_candidates_comparison.png")
    plt.close()


def export_results(rankings: dict, comparison_df: pd.DataFrame,
                  output_dir: str) -> None:
    """
    Export results to CSV files.
    
    Args:
        rankings (dict): Rankings from each model
        comparison_df (pd.DataFrame): Model comparison results
        output_dir (str): Directory to save results
    """
    logger.info("Exporting results...")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Save model comparison
    comparison_df.to_csv(os.path.join(output_dir, 'model_comparison.csv'))
    logger.info("Saved: model_comparison.csv")
    
    # Save rankings from each model
    for model_name, ranked_df in rankings.items():
        filename = f"rankings_{model_name.lower().replace(' ', '_')}.csv"
        ranked_df[['filename', 'category'] + 
                 [col for col in ranked_df.columns if 'score' in col.lower()]].to_csv(
            os.path.join(output_dir, filename),
            index=False
        )
        logger.info(f"Saved: {filename}")
    
    logger.info(f"Results exported to {output_dir}")


def main():
    """Main pipeline execution."""
    parser = argparse.ArgumentParser(
        description='Resume Screening Pipeline - Integrating Kaggle approach'
    )
    parser.add_argument(
        '--data_path',
        type=str,
        default='./data/resumes',
        help='Path to resume data directory'
    )
    parser.add_argument(
        '--csv_path',
        type=str,
        default=None,
        help='Path to Resume.csv file (optional - for data integration)'
    )
    parser.add_argument(
        '--job_desc',
        type=str,
        default='./job_description.txt',
        help='Path to job description file'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='./pipeline_results',
        help='Output directory for results'
    )
    parser.add_argument(
        '--relevant_categories',
        type=str,
        nargs='+',
        default=['ENGINEERING', 'INFORMATION-TECHNOLOGY'],
        help='Categories to consider as relevant for evaluation'
    )
    parser.add_argument(
        '--k',
        type=int,
        default=10,
        help='K value for Precision@K and Recall@K metrics'
    )
    
    args = parser.parse_args()
    
    try:
        logger.info("="*70)
        logger.info("RESUME SCREENING PIPELINE - KAGGLE INTEGRATION")
        logger.info("="*70)
        
        # Step 0: Optional CSV data integration
        if args.csv_path:
            logger.info("\n[STEP 0] Integrating CSV Data")
            if integrate_csv_data(args.csv_path, args.data_path):
                logger.info("CSV data integration complete")
            else:
                logger.warning("CSV data integration failed, continuing with existing data")
        
        # Step 1: Data preparation
        logger.info("\n[STEP 1] Data Preparation")
        df, job_desc, job_skills = prepare_data(args.data_path, args.job_desc)
        
        if df.empty:
            logger.error("No resumes loaded from data directory")
            logger.info(f"Please check the data path: {args.data_path}")
            return
        
        # Step 2: Initialize BERT model
        logger.info("\n[STEP 2] Initializing Models")
        initialize_bert_model()
        logger.info("BERT model initialized")
        
        # Step 3: Run ranking algorithms
        logger.info("\n[STEP 3] Running Ranking Algorithms")
        rankings = run_ranking_pipeline(df, job_desc, job_skills)
        
        # Step 4: Evaluate rankings
        logger.info("\n[STEP 4] Evaluating Rankings")
        comparison_df = evaluate_rankings(
            rankings,
            args.relevant_categories,
            args.k
        )
        
        # Step 5: Visualize results
        logger.info("\n[STEP 5] Creating Visualizations")
        visualize_results(comparison_df, rankings, args.output)
        
        # Step 6: Export results
        logger.info("\n[STEP 6] Exporting Results")
        export_results(rankings, comparison_df, args.output)
        
        logger.info("\n" + "="*70)
        logger.info("PIPELINE COMPLETE!")
        logger.info(f"Results saved to: {args.output}")
        logger.info("="*70)
        
        # Print summary
        print("\n" + "="*70)
        print("MODEL PERFORMANCE SUMMARY")
        print("="*70)
        print(comparison_df)
        print("="*70)
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
