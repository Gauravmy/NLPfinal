"""
Resume Screening System - Production-Ready Streamlit Application

Advanced resume screening and candidate ranking powered by NLP.
Features 4 ranking models, skill extraction, evaluation metrics, and more.

Author: AI/ML Engineering Team
Version: 3.0.0 (Production - Streamlit Cloud)
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Fast imports first
from src.text_preprocessing import preprocess_text
from src.skill_extractor import extract_skills, extract_job_skills

# Lazy import for heavy modules
def get_heavy_imports():
    """Lazy load heavy modules only when needed"""
    try:
        from src.ranking_engine import rank_candidates, get_top_candidates
        from src.model_comparison import (
            rank_by_tfidf, rank_by_bert, rank_by_hybrid, rank_by_deep_ensemble
        )
        from src.similarity_model import initialize_bert_model
        return {
            'rank_candidates': rank_candidates,
            'get_top_candidates': get_top_candidates,
            'rank_by_tfidf': rank_by_tfidf,
            'rank_by_bert': rank_by_bert,
            'rank_by_hybrid': rank_by_hybrid,
            'rank_by_deep_ensemble': rank_by_deep_ensemble,
            'initialize_bert_model': initialize_bert_model
        }
    except Exception as e:
        return None

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# ============================================================================
# PAGE CONFIGURATION WITH ACCESSIBILITY
# ============================================================================

st.set_page_config(
    page_title="Resume Screening Pro",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com',
        'Report a bug': 'https://github.com',
        'About': "Resume Screening Pro v3.0 - Streamlit Cloud Ready"
    }
)

# ============================================================================
# MODERN, ACCESSIBLE CUSTOM STYLING
# ============================================================================

st.markdown("""
    <style>
        .main {
            padding: 2rem;
            max-width: 1400px;
            margin: 0 auto;
            background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
        }
        
        h1 {
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
            font-size: 2.5rem;
            font-weight: 700;
            line-height: 1.2;
        }
        
        h2 {
            color: #1f77b4;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            font-size: 1.8rem;
            font-weight: 600;
        }
        
        h3 {
            color: #333;
            margin-top: 1rem;
            margin-bottom: 0.75rem;
            font-size: 1.3rem;
            font-weight: 600;
        }
        
        .metric-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border: 2px solid transparent;
            transition: all 0.3s ease;
        }
        
        .metric-box:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.15);
        }
        
        .card {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: box-shadow 0.3s ease;
        }
        
        .card:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .success-box {
            background: #d4edda;
            color: #155724;
            padding: 1rem;
            border-radius: 5px;
            border-left: 5px solid #28a745;
            margin: 1rem 0;
            font-weight: 500;
        }
        
        .warning-box {
            background: #fff3cd;
            color: #856404;
            padding: 1rem;
            border-radius: 5px;
            border-left: 5px solid #ffc107;
            margin: 1rem 0;
            font-weight: 500;
        }
        
        .error-box {
            background: #f8d7da;
            color: #721c24;
            padding: 1rem;
            border-radius: 5px;
            border-left: 5px solid #dc3545;
            margin: 1rem 0;
            font-weight: 500;
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            min-height: 44px;
            width: 100%;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        .stButton > button:focus {
            outline: 3px solid #667eea;
            outline-offset: 2px;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
            border-bottom: 2px solid #e0e0e0;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            border-radius: 5px 5px 0 0;
        }
        
        .stDataFrame {
            font-size: 0.95rem;
            overflow: auto;
        }
        
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f8f9fa 0%, #f0f0f0 100%);
            border-right: 1px solid #e0e0e0;
        }
        
        .stTextInput input, .stTextArea textarea, .stSelectbox select {
            border-radius: 5px;
            border: 1px solid #ddd;
            padding: 0.75rem;
            font-size: 1rem;
        }
        
        .stTextInput input:focus, 
        .stTextArea textarea:focus, 
        .stSelectbox select:focus {
            outline: 2px solid #667eea;
            outline-offset: 2px;
            border-color: #667eea;
        }
        
        .footer {
            text-align: center;
            color: #666;
            font-size: 0.85rem;
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid #e0e0e0;
        }
        
        hr {
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, #ddd, transparent);
        }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# CACHE & SESSION STATE
# ============================================================================

@st.cache_resource
def load_bert_model():
    """Load BERT model once and cache it."""
    heavy_imports = get_heavy_imports()
    if heavy_imports:
        try:
            heavy_imports['initialize_bert_model']()
            return True
        except Exception as e:
            st.warning(f"BERT model loading delayed: {str(e)[:50]}")
            return False
    return False

if 'df_resumes' not in st.session_state:
    st.session_state.df_resumes = pd.DataFrame()
if 'rankings' not in st.session_state:
    st.session_state.rankings = {}
if 'heavy_imports' not in st.session_state:
    st.session_state.heavy_imports = None

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

@st.cache_data
def load_resumes_from_directory(data_path: str) -> pd.DataFrame:
    """Load resumes from directory structure."""
    try:
        data = []
        data_path = Path(data_path)
        
        if not data_path.exists():
            return pd.DataFrame()
        
        for category_dir in data_path.iterdir():
            if category_dir.is_dir():
                for resume_file in category_dir.glob('*.txt'):
                    try:
                        with open(resume_file, 'r', encoding='utf-8') as f:
                            text = f.read()
                        data.append({
                            'filename': resume_file.name,
                            'category': category_dir.name,
                            'resume_text': text
                        })
                    except Exception as e:
                        logger.warning(f"Error reading {resume_file}: {e}")
                        continue
        
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
        logger.error(f"Error loading resumes: {e}")
        return pd.DataFrame()

def create_metric_card(label: str, value: str, color: str = "#667eea"):
    """Create a styled metric card."""
    st.markdown(f"""
        <div class="metric-box" style="background: linear-gradient(135deg, {color} 0%, #764ba2 100%);">
            <h3 style="margin: 0; font-size: 0.9rem; opacity: 0.95;">{label}</h3>
            <h2 style="margin: 0.5rem 0; color: white; font-size: 2rem;">{value}</h2>
        </div>
    """, unsafe_allow_html=True)

def export_to_csv(df: pd.DataFrame) -> bytes:
    """Export DataFrame to CSV."""
    return df.to_csv(index=False).encode('utf-8')

def export_to_excel(df: pd.DataFrame) -> bytes:
    """Export DataFrame to Excel."""
    buffer = BytesIO()
    df.to_excel(buffer, index=False, sheet_name='Rankings')
    buffer.seek(0)
    return buffer.getvalue()

# ============================================================================
# PAGE LAYOUT
# ============================================================================

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<h1>Resume Screening Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>AI-powered resume screening with 4 ranking models</p>", unsafe_allow_html=True)

st.markdown("---")

#SIDEBAR
with st.sidebar:
    st.markdown("### Configuration")
    
    st.subheader("Data Source")
    data_path = st.text_input(
        "Resume Directory",
        value="./data/resumes",
        help="Path containing resume files by category"
    )
    
    if st.button("Load Resumes", use_container_width=True):
        st.session_state.df_resumes = load_resumes_from_directory(data_path)
        if not st.session_state.df_resumes.empty:
            st.success(f"Loaded {len(st.session_state.df_resumes)} resumes")
        else:
            st.error("No resumes found")
    
    st.divider()
    
    st.subheader("Job Description")
    job_description_input = st.text_area(
        "Enter Job Requirements",
        value="",
        height=150,
        placeholder="Paste job description...",
        label_visibility="collapsed"
    )
    
    st.divider()
    
    st.subheader("Models")
    selected_models = st.multiselect(
        "Select Models",
        options=["TF-IDF", "BERT", "Hybrid", "Deep Ensemble"],
        default=["Deep Ensemble"],
        help="Choose ranking models to use"
    )
    
    st.divider()
    
    st.subheader("Results")
    results_k = st.slider("Top-K", 5, 50, 10, 5)
    
    if not st.session_state.df_resumes.empty:
        available_categories = st.session_state.df_resumes['category'].unique().tolist()
        filter_categories = st.multiselect(
            "Filter Categories",
            options=sorted(available_categories),
            help="Optional category filter"
        )
    else:
        filter_categories = []
    
    st.divider()
    with st.expander("About"):
        st.markdown("""
        **Resume Screening Pro v3.0**
        
        Features:
        - 4 Ranking Models
        - Skill Extraction
        - Performance Metrics
        - Multi-format Export
        """)

# Main CONTENT
if st.session_state.df_resumes.empty:
    st.info("Load resumes from the sidebar to begin")
elif not job_description_input.strip():
    st.info("Enter a job description in the sidebar")
else:
    tab1, tab2, tab3, tab4 = st.tabs(["Rankings", "Analysis", "Comparison", "Export"])
    
    with tab1:
        st.markdown("## Candidate Rankings")
        
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            df = st.session_state.df_resumes.copy()
            df['cleaned_text'] = df['resume_text'].apply(preprocess_text)
            progress_bar.progress(20)
            
            status_text.text("Extracting skills...")
            df['skills'] = df['cleaned_text'].apply(extract_skills)
            progress_bar.progress(40)
            
            status_text.text("Processing job...")
            clean_job_desc = preprocess_text(job_description_input)
            job_skills = extract_job_skills(job_description_input)
            progress_bar.progress(60)
            
            if "BERT" in selected_models or "Deep Ensemble" in selected_models:
                load_bert_model()
            progress_bar.progress(80)
            
            # Load heavy imports when needed
            if st.session_state.heavy_imports is None:
                st.session_state.heavy_imports = get_heavy_imports()
            
            heavy_imports = st.session_state.heavy_imports
            if not heavy_imports:
                st.error("Required ranking models unavailable. Please refresh the page.")
                st.stop()
            
            st.session_state.rankings = {}
            
            if "TF-IDF" in selected_models:
                status_text.text("Running TF-IDF...")
                try:
                    st.session_state.rankings['TF-IDF'] = heavy_imports['rank_by_tfidf'](df, clean_job_desc)
                except Exception as e:
                    st.warning(f"TF-IDF failed: {str(e)[:50]}")
            
            if "BERT" in selected_models:
                status_text.text("Running BERT...")
                try:
                    st.session_state.rankings['BERT'] = heavy_imports['rank_by_bert'](df, clean_job_desc)
                except Exception as e:
                    st.warning(f"BERT failed: {str(e)[:50]}")
            
            if "Hybrid" in selected_models:
                status_text.text("Running Hybrid...")
                try:
                    st.session_state.rankings['Hybrid'] = heavy_imports['rank_by_hybrid'](df, clean_job_desc, job_skills)
                except Exception as e:
                    st.warning(f"Hybrid failed: {str(e)[:50]}")
            
            if "Deep Ensemble" in selected_models:
                status_text.text("Running Ensemble...")
                try:
                    st.session_state.rankings['Deep Ensemble'] = heavy_imports['rank_by_deep_ensemble'](
                        df, clean_job_desc, job_skills
                    )
                except Exception as e:
                    st.warning(f"Deep Ensemble failed: {str(e)[:50]}")
            
            progress_bar.progress(100)
            status_text.empty()
            progress_bar.empty()
            
            st.success(f"Complete! Analyzed {len(df)} resumes")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                create_metric_card("Total", str(len(df)))
            with col2:
                create_metric_card("Categories", str(df['category'].nunique()), "#2196F3")
            with col3:
                create_metric_card("Avg Skills", f"{df['skills'].apply(len).mean():.1f}", "#4CAF50")
            with col4:
                create_metric_card("Job Skills", str(len(job_skills)), "#FF9800")
            
            st.divider()
            
            for model_name, ranked_df in st.session_state.rankings.items():
                st.subheader(f"{model_name} Rankings")
                
                score_columns = [col for col in ranked_df.columns if 'score' in col.lower()]
                if score_columns:
                    score_col = score_columns[0]
                    
                    if filter_categories:
                        ranked_df = ranked_df[ranked_df['category'].isin(filter_categories)]
                    
                    display_df = ranked_df.head(results_k)[['filename', 'category', score_col]].copy()
                    display_df = display_df.reset_index(drop=True)
                    display_df.index = display_df.index + 1
                    display_df.columns = ['Filename', 'Category', 'Score']
                    display_df['Score'] = display_df['Score'].apply(lambda x: f"{x:.4f}")
                    
                    st.dataframe(display_df, use_container_width=True)
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
            logger.exception(e)
    
    with tab2:
        st.markdown("## Analysis")
        
        if st.session_state.rankings:
            try:
                df = st.session_state.df_resumes.copy()
                df['cleaned_text'] = df['resume_text'].apply(preprocess_text)
                df['skills'] = df['cleaned_text'].apply(extract_skills)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Category Distribution")
                    cat_counts = df['category'].value_counts()
                    fig, ax = plt.subplots(figsize=(10, 6))
                    cat_counts.plot(kind='barh', ax=ax, color='#667eea')
                    ax.set_xlabel('Count')
                    ax.set_title('Resumes by Category')
                    st.pyplot(fig)
                
                with col2:
                    st.subheader("Skill Distribution")
                    all_skills = []
                    for skills in df['skills']:
                        all_skills.extend(skills)
                    
                    if all_skills:
                        skill_counts = pd.Series(all_skills).value_counts().head(15)
                        fig, ax = plt.subplots(figsize=(10, 6))
                        skill_counts.plot(kind='barh', ax=ax, color='#764ba2')
                        ax.set_xlabel('Frequency')
                        ax.set_title('Top 15 Skills')
                        st.pyplot(fig)
                
                st.divider()
                st.subheader("Job Skills")
                
                clean_job_desc = preprocess_text(job_description_input)
                job_skills = extract_job_skills(job_description_input)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    create_metric_card("Required", str(len(job_skills)))
                with col2:
                    candidates_with_skills = sum([
                        any(skill in resume_skills for skill in job_skills)
                        for resume_skills in df['skills']
                    ])
                    create_metric_card("Match", str(candidates_with_skills), "#4CAF50")
                with col3:
                    match_percent = (candidates_with_skills / len(df) * 100) if len(df) > 0 else 0
                    create_metric_card("Rate", f"{match_percent:.1f}%", "#FF9800")
            
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    with tab3:
        st.markdown("## Model Comparison")
        
        if len(st.session_state.rankings) > 1:
            try:
                comparison_data = []
                
                for model_name, ranked_df in st.session_state.rankings.items():
                    score_columns = [col for col in ranked_df.columns if 'score' in col.lower()]
                    if score_columns:
                        score_col = score_columns[0]
                        comparison_data.append({
                            'Model': model_name,
                            'Top Score': ranked_df[score_col].iloc[0] if len(ranked_df) > 0 else 0,
                            'Avg Score': ranked_df[score_col].mean(),
                            'Candidates': len(ranked_df)
                        })
                
                if comparison_data:
                    comp_df = pd.DataFrame(comparison_data)
                    st.dataframe(comp_df, use_container_width=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig, ax = plt.subplots(figsize=(8, 5))
                        ax.bar(comp_df['Model'], comp_df['Avg Score'], color='#667eea')
                        ax.set_ylabel('Average Score')
                        ax.set_title('Avg Score by Model')
                        st.pyplot(fig)
                    
                    with col2:
                        fig, ax = plt.subplots(figsize=(8, 5))
                        ax.bar(comp_df['Model'], comp_df['Top Score'], color='#764ba2')
                        ax.set_ylabel('Top Score')
                        ax.set_title('Best Score by Model')
                        st.pyplot(fig)
            
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.info("Run multiple models to compare")
    
    with tab4:
        st.markdown("## Export")
        
        if st.session_state.rankings:
            try:
                all_rankings = []
                for model_name, ranked_df in st.session_state.rankings.items():
                    score_columns = [col for col in ranked_df.columns if 'score' in col.lower()]
                    if score_columns:
                        score_col = score_columns[0]
                        export_df = ranked_df[['filename', 'category', score_col]].copy()
                        export_df['model'] = model_name
                        export_df.columns = ['Filename', 'Category', 'Score', 'Model']
                        all_rankings.append(export_df)
                
                if all_rankings:
                    export_data = pd.concat(all_rankings, ignore_index=True)
                    
                    csv_data = export_to_csv(export_data)
                    st.download_button(
                        label="CSV",
                        data=csv_data,
                        file_name=f"rankings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                    
                    try:
                        excel_data = export_to_excel(export_data)
                        st.download_button(
                            label="Excel",
                            data=excel_data,
                            file_name=f"rankings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    except Exception as e:
                        logger.warning(f"Excel unavailable: {e}")
                    
                    st.divider()
                    st.dataframe(export_data.head(20), use_container_width=True)
            
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.info("Process candidates first")

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.85rem; padding: 2rem 0;'>
    <p>Resume Screening Pro v3.0 | Production Ready</p>
</div>
""", unsafe_allow_html=True)
