"""
Data Integration Module

This module integrates resume data from multiple sources:
1. PDF files from archive data directory
2. CSV file with structured resume data and categories

Provides utilities to load, merge, and manage combined datasets.
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataIntegrator:
    """
    Integrates resume data from multiple sources.
    """
    
    def __init__(self, csv_path: str = None, pdf_dir: str = None,
                 local_pdf_dir: str = './data/resumes'):
        """
        Initialize data integrator.
        
        Args:
            csv_path (str): Path to Resume.csv file
            pdf_dir (str): Path to PDF resume data directory
            local_pdf_dir (str): Local path to copy PDFs to
        """
        self.csv_path = csv_path
        self.pdf_dir = pdf_dir
        self.local_pdf_dir = local_pdf_dir
        self.df_csv = None
        self.df_combined = None
        
    def load_csv_data(self) -> pd.DataFrame:
        """
        Load Resume.csv data.
        
        Returns:
            pd.DataFrame: DataFrame with resume data and categories
        """
        try:
            if not self.csv_path:
                logger.warning("CSV path not set")
                return pd.DataFrame()
            
            logger.info(f"Loading CSV data from {self.csv_path}...")
            df = pd.read_csv(self.csv_path)
            
            logger.info(f"Loaded {len(df)} records from CSV")
            logger.info(f"Categories: {df['Category'].unique().tolist()}")
            logger.info(f"Columns: {df.columns.tolist()}")
            
            self.df_csv = df
            return df
            
        except Exception as e:
            logger.error(f"Error loading CSV data: {e}")
            return pd.DataFrame()
    
    def create_structured_dataframe(self) -> pd.DataFrame:
        """
        Create a structured DataFrame from CSV data suitable for screening.
        
        Returns:
            pd.DataFrame: DataFrame with columns: filename, category, resume_text
        """
        try:
            if self.df_csv is None or self.df_csv.empty:
                logger.warning("CSV data not loaded")
                return pd.DataFrame()
            
            logger.info("Creating structured DataFrame from CSV...")
            
            # Create new dataframe with standardized columns
            df_structured = pd.DataFrame({
                'id': self.df_csv['ID'],
                'filename': 'csv_' + self.df_csv['ID'].astype(str) + '.txt',
                'category': self.df_csv['Category'],
                'resume_text': self.df_csv['Resume_str'],
                'resume_html': self.df_csv['Resume_html'],
                'source': 'csv'
            })
            
            logger.info(f"Created structured DataFrame with {len(df_structured)} rows")
            self.df_combined = df_structured
            
            return df_structured
            
        except Exception as e:
            logger.error(f"Error creating structured DataFrame: {e}")
            return pd.DataFrame()
    
    def save_csv_resumes_as_text(self, output_dir: str = None) -> int:
        """
        Extract resume texts from CSV and save as individual text files.
        Useful for processing alongside PDF-based resumes.
        
        Args:
            output_dir (str): Directory to save text files
            
        Returns:
            int: Number of files saved
        """
        try:
            if output_dir is None:
                output_dir = os.path.join(self.local_pdf_dir, 'csv_resumes')
            
            os.makedirs(output_dir, exist_ok=True)
            
            if self.df_csv is None or self.df_csv.empty:
                logger.warning("CSV data not loaded")
                return 0
            
            logger.info(f"Saving {len(self.df_csv)} resumes as text files...")
            
            saved_count = 0
            for idx, row in tqdm(self.df_csv.iterrows(), total=len(self.df_csv)):
                try:
                    filename = os.path.join(
                        output_dir,
                        f"resume_{row['ID']}.txt"
                    )
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(row['Resume_str'])
                    
                    saved_count += 1
                    
                except Exception as e:
                    logger.warning(f"Error saving resume {row['ID']}: {e}")
                    continue
            
            logger.info(f"Saved {saved_count} resume text files to {output_dir}")
            return saved_count
            
        except Exception as e:
            logger.error(f"Error saving resume text files: {e}")
            return 0
    
    def organize_csv_resumes_by_category(self, output_dir: str = None) -> int:
        """
        Organize CSV resume text files into category subdirectories.
        Matches the directory structure expected by the pipeline.
        
        Args:
            output_dir (str): Base output directory
            
        Returns:
            int: Number of files organized
        """
        try:
            if output_dir is None:
                output_dir = self.local_pdf_dir
            
            if self.df_csv is None or self.df_csv.empty:
                logger.warning("CSV data not loaded")
                return 0
            
            logger.info(f"Organizing {len(self.df_csv)} resumes by category...")
            
            organized_count = 0
            for idx, row in tqdm(self.df_csv.iterrows(), total=len(self.df_csv)):
                try:
                    category = row['Category']
                    category_dir = os.path.join(output_dir, category)
                    os.makedirs(category_dir, exist_ok=True)
                    
                    filename = os.path.join(
                        category_dir,
                        f"csv_{row['ID']}.txt"
                    )
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(row['Resume_str'])
                    
                    organized_count += 1
                    
                except Exception as e:
                    logger.warning(f"Error organizing resume {row['ID']}: {e}")
                    continue
            
            logger.info(f"Organized {organized_count} resumes by category in {output_dir}")
            return organized_count
            
        except Exception as e:
            logger.error(f"Error organizing resumes: {e}")
            return 0
    
    def get_summary_statistics(self) -> dict:
        """
        Get summary statistics of the integrated data.
        
        Returns:
            dict: Summary statistics
        """
        try:
            if self.df_csv is None or self.df_csv.empty:
                return {}
            
            stats = {
                'total_resumes': len(self.df_csv),
                'categories': self.df_csv['Category'].nunique(),
                'category_distribution': self.df_csv['Category'].value_counts().to_dict(),
                'avg_resume_length': self.df_csv['Resume_str'].str.len().mean(),
                'max_resume_length': self.df_csv['Resume_str'].str.len().max(),
                'min_resume_length': self.df_csv['Resume_str'].str.len().min()
            }
            
            logger.info(f"Data Summary: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {}
    
    def export_combined_data(self, output_path: str = 'combined_resumes.csv') -> bool:
        """
        Export combined structured data to CSV.
        
        Args:
            output_path (str): Path to save combined data
            
        Returns:
            bool: Success status
        """
        try:
            if self.df_combined is None or self.df_combined.empty:
                logger.warning("No combined data to export")
                return False
            
            self.df_combined.to_csv(output_path, index=False)
            logger.info(f"Exported combined data to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting combined data: {e}")
            return False


def quick_integrate_data(csv_path: str, output_dir: str = './data/resumes') -> Tuple[int, dict]:
    """
    Quick integration function to process CSV resume data.
    
    Args:
        csv_path (str): Path to Resume.csv
        output_dir (str): Output directory for organized resumes
        
    Returns:
        Tuple[int, dict]: Number of resumes processed and statistics
    """
    try:
        logger.info("="*70)
        logger.info("RESUME DATA INTEGRATION")
        logger.info("="*70)
        
        integrator = DataIntegrator(csv_path=csv_path, local_pdf_dir=output_dir)
        
        # Load CSV data
        logger.info("\n[1/3] Loading CSV data...")
        integrator.load_csv_data()
        
        # Get statistics
        logger.info("\n[2/3] Analyzing data...")
        stats = integrator.get_summary_statistics()
        
        # Organize by category
        logger.info("\n[3/3] Organizing resumes by category...")
        count = integrator.organize_csv_resumes_by_category(output_dir)
        
        logger.info("\n" + "="*70)
        logger.info(f"INTEGRATION COMPLETE!")
        logger.info(f"Processed: {count} resumes")
        logger.info(f"Categories: {stats.get('categories', 0)}")
        logger.info("="*70)
        
        return count, stats
        
    except Exception as e:
        logger.error(f"Integration failed: {e}")
        return 0, {}


if __name__ == '__main__':
    # Example usage
    csv_path = r"c:\Users\hp\Downloads\archive (19)\Resume\Resume.csv"
    output_dir = r"c:\Users\hp\Desktop\NLPpro\resume_screening_project\data\resumes"
    
    count, stats = quick_integrate_data(csv_path, output_dir)
    
    if count > 0:
        print(f"\nSuccessfully integrated {count} resumes!")
        print(f"Category Distribution:")
        for cat, cnt in stats.get('category_distribution', {}).items():
            print(f"  - {cat}: {cnt} resumes")
