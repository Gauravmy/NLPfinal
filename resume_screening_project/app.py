"""
Resume Screening System - Production-Ready Streamlit Application

Advanced resume screening and candidate ranking powered by NLP.
Features 4 ranking models, skill extraction, evaluation metrics, and more.

Author: AI/ML Engineering Team
Version: 4.0.0 (Enhanced with Manual Upload & Advanced Analytics)
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
import re
import tempfile

warnings.filterwarnings('ignore')

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.skill_extractor import extract_skills
from src.text_preprocessing import preprocess_text

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
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');
        
        * {
            font-family: 'Inter', 'Poppins', sans-serif !important;
        }
        
        .main {
            padding: 0;
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            min-height: 100vh;
        }
        
        .stApp {
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        }
        
        h1 {
            color: #ffffff;
            text-align: center;
            margin-bottom: 0.5rem;
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
        }
        
        .subtitle {
            color: #b0b0c9;
            text-align: center;
            font-size: 1.1rem;
            margin-bottom: 2rem;
            font-weight: 400;
        }
        
        h2 {
            color: #ffffff;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            font-size: 1.8rem;
            font-weight: 600;
            border-bottom: 3px solid;
            border-image: linear-gradient(135deg, #667eea 0%, #764ba2 100%) 1;
            padding-bottom: 0.5rem;
        }
        
        h3 {
            color: #e0e0ff;
            margin-top: 1rem;
            margin-bottom: 0.75rem;
            font-size: 1.3rem;
            font-weight: 600;
        }
        
        /* Premium Metric Cards */
        .metric-box {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.95) 0%, rgba(118, 75, 162, 0.95) 100%);
            color: white;
            padding: 2rem;
            border-radius: 16px;
            margin: 1rem 0;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.25);
            border: 1px solid rgba(255, 255, 255, 0.18);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(10px);
            position: relative;
            overflow: hidden;
        }
        
        .metric-box::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.6s ease;
        }
        
        .metric-box:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 16px 48px rgba(102, 126, 234, 0.4);
        }
        
        .metric-box:hover::before {
            left: 100%;
        }
        
        .premium-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(245,247,250,0.98) 100%);
            border: 1px solid rgba(102, 126, 234, 0.2);
            border-radius: 16px;
            padding: 2rem;
            margin: 1.5rem 0;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .premium-card:hover {
            box-shadow: 0 16px 48px rgba(102, 126, 234, 0.25);
            transform: translateY(-4px);
            border-color: rgba(102, 126, 234, 0.5);
        }
        
        .success-badge {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 10px;
            border-left: 5px solid #047857;
            margin: 1rem 0;
            font-weight: 500;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
        }
        
        .warning-badge {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 10px;
            border-left: 5px solid #b45309;
            margin: 1rem 0;
            font-weight: 500;
            box-shadow: 0 4px 12px rgba(245, 158, 11, 0.2);
        }
        
        .error-badge {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 10px;
            border-left: 5px solid #b91c1c;
            margin: 1rem 0;
            font-weight: 500;
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
        }
        
        /* Premium Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 0.75rem 2rem !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            cursor: pointer !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            min-height: 44px !important;
            width: 100% !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5) !important;
        }
        
        /* Premium Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
            border-bottom: 2px solid rgba(102, 126, 234, 0.2);
            background: linear-gradient(90deg, rgba(102,126,234,0.05) 0%, transparent 100%);
            padding: 1rem;
            border-radius: 12px;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            border-radius: 10px;
            background: rgba(102, 126, 234, 0.1);
            color: #b0b0c9;
            transition: all 0.3s ease;
            border: 1px solid rgba(102, 126, 234, 0.2);
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        /* Input Fields */
        .stTextInput input, .stTextArea textarea, .stSelectbox select {
            background: rgba(255, 255, 255, 0.9) !important;
            border: 1px solid rgba(102, 126, 234, 0.3) !important;
            border-radius: 10px !important;
            padding: 0.75rem !important;
            font-size: 1rem !important;
            color: #333 !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextInput input:focus, 
        .stTextArea textarea:focus, 
        .stSelectbox select:focus {
            outline: none !important;
            border-color: #667eea !important;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
            background: white !important;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(48, 43, 99, 0.7) 0%, rgba(36, 36, 62, 0.7) 100%);
            border-right: 2px solid rgba(102, 126, 234, 0.2);
        }
        
        [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
            color: #e0e0ff !important;
        }
        
        /* Data Tables */
        .stDataFrame {
            font-size: 0.95rem;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        
        /* Footer */
        .footer {
            text-align: center;
            color: #b0b0c9;
            font-size: 0.9rem;
            margin-top: 3rem;
            padding: 2rem;
            border-top: 1px solid rgba(102, 126, 234, 0.2);
            background: rgba(48, 43, 99, 0.3);
            border-radius: 12px;
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
if 'job_skills_extracted' not in st.session_state:
    st.session_state.job_skills_extracted = []
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'skill_matching_data' not in st.session_state:
    st.session_state.skill_matching_data = {}

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
            <div style='margin: 0; font-size: 0.9rem; opacity: 0.95; font-weight: 500;'>{label}</div>
            <div style='margin: 0.5rem 0; color: white; font-size: 2.2rem; font-weight: 700;'>{value}</div>
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

def process_resume_file(uploaded_file) -> dict:
    """Process uploaded resume file (PDF, DOCX, TXT)."""
    try:
        filename = uploaded_file.name
        
        if filename.endswith('.txt'):
            text = uploaded_file.read().decode('utf-8')
        elif filename.endswith('.pdf'):
            try:
                import pdfplumber
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as f:
                    f.write(uploaded_file.getbuffer())
                    f.flush()
                    with pdfplumber.open(f.name) as pdf:
                        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
                os.unlink(f.name)
            except Exception as e:
                logger.warning(f"PDF processing failed: {e}")
                text = ""
        elif filename.endswith('.docx'):
            try:
                from docx import Document
                with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as f:
                    f.write(uploaded_file.getbuffer())
                    f.flush()
                    doc = Document(f.name)
                    text = "\n".join([para.text for para in doc.paragraphs])
                os.unlink(f.name)
            except Exception as e:
                logger.warning(f"DOCX processing failed: {e}")
                text = ""
        else:
            return None
        
        return {
            'filename': filename,
            'resume_text': text,
            'category': 'Uploaded',
            'upload_date': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        return None

def calculate_skill_match_percentage(resume_skills, job_skills):
    """Calculate percentage of job skills matched in resume."""
    if not job_skills:
        return 0
    matched = sum(1 for skill in job_skills if skill.lower() in [s.lower() for s in resume_skills])
    return (matched / len(job_skills)) * 100

def calculate_required_vs_matched(resume_skills, job_skills):
    """Returns (matched_count, required_count)."""
    if not job_skills:
        return 0, 0
    matched = sum(1 for skill in job_skills if skill.lower() in [s.lower() for s in resume_skills])
    return matched, len(job_skills)

def get_rating_stars(percentage):
    """Convert percentage to star rating."""
    if percentage >= 90:
        return "⭐⭐⭐⭐⭐", "Excellent"
    elif percentage >= 75:
        return "⭐⭐⭐⭐", "Very Good"
    elif percentage >= 60:
        return "⭐⭐⭐", "Good"
    elif percentage >= 40:
        return "⭐⭐", "Fair"
    else:
        return "⭐", "Poor"

def create_detailed_candidate_card(index, candidate_data, job_skills, df_with_skills):
    """Create a detailed candidate comparison card."""
    filename = candidate_data['filename']
    category = candidate_data.get('category', 'N/A')
    skills = df_with_skills[df_with_skills['filename'] == filename]['skills'].values[0] if 'skills' in df_with_skills.columns else []
    
    match_count, total_required = calculate_required_vs_matched(skills, job_skills)
    match_percentage = calculate_skill_match_percentage(skills, job_skills)
    stars, rating = get_rating_stars(match_percentage)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"""
        **#{index} - {filename}**  
        Category: `{category}`
        """)
    
    with col2:
        st.metric("Match %", f"{match_percentage:.1f}%")
    
    with col3:
        st.markdown(f"<div style='text-align: center; font-size: 1.5rem;'>{stars}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center; font-size: 0.9rem; color: #666;'>{rating}</div>", unsafe_allow_html=True)
    
    # Matched Skills
    if skills:
        matched_skills = [s for s in job_skills if s.lower() in [sk.lower() for sk in skills]]
        missing_skills = [s for s in job_skills if s.lower() not in [sk.lower() for sk in skills]]
        
        col1, col2 = st.columns(2)
        
        with col1:
            if matched_skills:
                st.markdown(f"✅ **Matched Skills** ({len(matched_skills)}/{total_required})")
                for skill in matched_skills[:8]:
                    st.markdown(f"- {skill}")
                if len(matched_skills) > 8:
                    st.markdown(f"- +{len(matched_skills) - 8} more...")
        
        with col2:
            if missing_skills:
                st.markdown(f"❌ **Missing Skills** ({len(missing_skills)}/{total_required})")
                for skill in missing_skills[:8]:
                    st.markdown(f"- {skill}")
                if len(missing_skills) > 8:
                    st.markdown(f"- +{len(missing_skills) - 8} more...")
    
    st.divider()

# ============================================================================
# PAGE LAYOUT
# ============================================================================

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1>📄 Resume Screening Pro</h1>
            <p class='subtitle'>✨ AI-Powered Intelligent Resume Screening & Candidate Ranking</p>
            <p style='color: #8b92d6; font-size: 0.95rem; margin-top: 1rem;'>
                🚀 Powered by BERT, TF-IDF, Hybrid & Deep Ensemble Models
            </p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Initialize sidebar variables
job_description_input = ""
filter_categories = []
selected_models = []
results_k = 10

#SIDEBAR
with st.sidebar:
    st.markdown("### Configuration")
    
    st.subheader("📄 Data Sources")
    
    # Option 1: Load from Directory
    st.markdown("**Option 1: Load from Directory**")
    data_path = st.text_input(
        "Resume Directory",
        value="./data/resumes",
        help="Path containing resume files by category"
    )
    
    if st.button("Load from Directory", use_container_width=True, key="load_dir"):
        st.session_state.df_resumes = load_resumes_from_directory(data_path)
        if not st.session_state.df_resumes.empty:
            st.success(f"✅ Loaded {len(st.session_state.df_resumes)} resumes")
        else:
            st.error("❌ No resumes found")
    
    st.divider()
    
    # Option 2: Manual Upload
    st.markdown("**Option 2: Upload Resumes Manually**")
    uploaded_files = st.file_uploader(
        "Upload Resume Files",
        type=["txt", "pdf", "docx"],
        accept_multiple_files=True,
        help="You can upload multiple resumes at once"
    )
    
    if uploaded_files:
        if st.button("Add Uploaded Resumes", use_container_width=True, key="load_upload"):
            new_resumes = []
            for uploaded_file in uploaded_files:
                resume_data = process_resume_file(uploaded_file)
                if resume_data and resume_data['resume_text'].strip():
                    new_resumes.append(resume_data)
            
            if new_resumes:
                new_df = pd.DataFrame(new_resumes)
                st.session_state.df_resumes = pd.concat(
                    [st.session_state.df_resumes, new_df],
                    ignore_index=True
                )
                st.success(f"✅ Added {len(new_resumes)} resumes! Total: {len(st.session_state.df_resumes)}")
            else:
                st.error("❌ Could not process any resumes")
    
    st.divider()
    
    # Current Resume Count
    if not st.session_state.df_resumes.empty:
        st.metric("Total Resumes", len(st.session_state.df_resumes))
        if st.button("Clear All Resumes", use_container_width=True, key="clear_all"):
            st.session_state.df_resumes = pd.DataFrame()
            st.session_state.rankings = {}
            st.session_state.analysis_complete = False
            st.rerun()
    
    st.divider()
    
    st.subheader("💼 Job Description")
    job_description_input = st.text_area(
        "Enter Job Requirements",
        value="",
        height=150,
        placeholder="Paste job description here...",
        label_visibility="collapsed"
    )
    
    st.divider()
    
    st.subheader("🤖 Models")
    selected_models = st.multiselect(
        "Select Models",
        options=["TF-IDF", "BERT", "Hybrid", "Deep Ensemble"],
        default=["Deep Ensemble"],
        help="Choose ranking models to use"
    )
    
    st.divider()
    
    st.subheader("📊 Results")
    results_k = st.slider("Top-K Results", 5, 50, 15, 5)
    
    if not st.session_state.df_resumes.empty:
        available_categories = st.session_state.df_resumes['category'].unique().tolist()
        filter_categories = st.multiselect(
            "Filter by Categories",
            options=sorted(available_categories),
            help="Optional category filter"
        )
    else:
        filter_categories = []
    
    st.divider()
    with st.expander("ℹ️ About"):
        st.markdown("""
        **Resume Screening Pro v4.0**
        
        ✨ Features:
        - 📤 Manual Resume Upload (TXT, PDF, DOCX)
        - 🎯 4 AI Ranking Models
        - 📈 Skill Matching %
        - ⭐ Star Ratings (0-5)
        - 📊 Advanced Analytics
        - 📁 Multi-format Export
        """)


# Main CONTENT
if st.session_state.df_resumes.empty:
    st.info("👉 Load or upload resumes from the sidebar to begin")
elif not job_description_input.strip():
    st.info("👉 Enter a job description in the sidebar")
else:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏆 Rankings", "🔍 Analysis", "⚖️ Comparison", "📋 Detailed View", "📥 Export"])
    
    with tab1:
        st.markdown("## 🏆 Candidate Rankings with Skill Matching")
        
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            df = st.session_state.df_resumes.copy()
            df['cleaned_text'] = df['resume_text'].apply(preprocess_text)
            progress_bar.progress(20)
            
            status_text.text("Extracting skills...")
            df['skills'] = df['cleaned_text'].apply(extract_skills)
            progress_bar.progress(40)
            
            status_text.text("Processing job description...")
            clean_job_desc = preprocess_text(job_description_input)
            job_skills = extract_skills(clean_job_desc)
            st.session_state.job_skills_extracted = job_skills
            progress_bar.progress(60)
            
            # Calculate skill matching for all candidates
            df['matched_skills'] = df['skills'].apply(
                lambda x: calculate_required_vs_matched(x, job_skills)[0]
            )
            df['total_required'] = len(job_skills)
            df['skill_match_percentage'] = df['skills'].apply(
                lambda x: calculate_skill_match_percentage(x, job_skills)
            )
            
            st.session_state.skill_matching_data = {
                'matched_skills': df['matched_skills'].to_dict(),
                'skill_match_percentage': df['skill_match_percentage'].to_dict(),
                'skills': df['skills'].to_dict(),
                'filenames': df['filename'].to_list()
            }
            
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
                status_text.text("Running TF-IDF Model...")
                try:
                    tfidf_results = heavy_imports['rank_by_tfidf'](df, clean_job_desc)
                    # Add skill matching to results
                    tfidf_results['skill_match_percentage'] = df.set_index('filename').loc[tfidf_results['filename'], 'skill_match_percentage'].values
                    tfidf_results['matched_skills'] = df.set_index('filename').loc[tfidf_results['filename'], 'matched_skills'].values
                    st.session_state.rankings['TF-IDF'] = tfidf_results
                except Exception as e:
                    st.warning(f"TF-IDF failed: {str(e)[:50]}")
            
            if "BERT" in selected_models:
                status_text.text("Running BERT Model...")
                try:
                    bert_results = heavy_imports['rank_by_bert'](df, clean_job_desc)
                    bert_results['skill_match_percentage'] = df.set_index('filename').loc[bert_results['filename'], 'skill_match_percentage'].values
                    bert_results['matched_skills'] = df.set_index('filename').loc[bert_results['filename'], 'matched_skills'].values
                    st.session_state.rankings['BERT'] = bert_results
                except Exception as e:
                    st.warning(f"BERT failed: {str(e)[:50]}")
            
            if "Hybrid" in selected_models:
                status_text.text("Running Hybrid Model...")
                try:
                    hybrid_results = heavy_imports['rank_by_hybrid'](df, clean_job_desc, job_skills)
                    hybrid_results['skill_match_percentage'] = df.set_index('filename').loc[hybrid_results['filename'], 'skill_match_percentage'].values
                    hybrid_results['matched_skills'] = df.set_index('filename').loc[hybrid_results['filename'], 'matched_skills'].values
                    st.session_state.rankings['Hybrid'] = hybrid_results
                except Exception as e:
                    st.warning(f"Hybrid failed: {str(e)[:50]}")
            
            if "Deep Ensemble" in selected_models:
                status_text.text("Running Deep Ensemble Model...")
                try:
                    ensemble_results = heavy_imports['rank_by_deep_ensemble'](df, clean_job_desc, job_skills)
                    ensemble_results['skill_match_percentage'] = df.set_index('filename').loc[ensemble_results['filename'], 'skill_match_percentage'].values
                    ensemble_results['matched_skills'] = df.set_index('filename').loc[ensemble_results['filename'], 'matched_skills'].values
                    st.session_state.rankings['Deep Ensemble'] = ensemble_results
                except Exception as e:
                    st.warning(f"Deep Ensemble failed: {str(e)[:50]}")
            
            progress_bar.progress(100)
            status_text.empty()
            progress_bar.empty()
            st.session_state.analysis_complete = True
            
            st.success(f"✅ Analysis Complete! Analyzed {len(df)} resumes")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                create_metric_card("Total Resumes", str(len(df)))
            with col2:
                create_metric_card("Categories", str(df['category'].nunique()), "#2196F3")
            with col3:
                create_metric_card("Required Skills", str(len(job_skills)), "#FF9800")
            with col4:
                avg_match = df['skill_match_percentage'].mean()
                create_metric_card("Avg Match %", f"{avg_match:.1f}%", "#4CAF50")
            
            st.divider()
            
            for model_name, ranked_df in st.session_state.rankings.items():
                st.subheader(f"🤖 {model_name} Rankings")
                
                score_columns = [col for col in ranked_df.columns if 'score' in col.lower()]
                if score_columns:
                    score_col = score_columns[0]
                    
                    if filter_categories:
                        ranked_df_filtered = ranked_df[ranked_df['category'].isin(filter_categories)]
                    else:
                        ranked_df_filtered = ranked_df
                    
                    display_df = ranked_df_filtered.head(results_k)[
                        ['filename', 'category', score_col, 'skill_match_percentage', 'matched_skills']
                    ].copy()
                    display_df = display_df.reset_index(drop=True)
                    display_df.index = display_df.index + 1
                    display_df.columns = ['Candidate', 'Category', 'Score', 'Skill Match %', 'Skills Matched']
                    display_df['Skill Match %'] = display_df['Skill Match %'].apply(lambda x: f"{x:.1f}%")
                    display_df['Skills Matched'] = display_df['Skills Matched'].apply(lambda x: f"{int(x)}/{len(job_skills)}")
                    
                    st.dataframe(display_df, use_container_width=True)
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            logger.exception(e)
    
    with tab2:
        st.markdown("## 🔍 Analysis & Insights")
        
        if st.session_state.analysis_complete:
            try:
                df = st.session_state.df_resumes.copy()
                df['cleaned_text'] = df['resume_text'].apply(preprocess_text)
                df['skills'] = df['cleaned_text'].apply(extract_skills)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📊 Category Distribution")
                    cat_counts = df['category'].value_counts()
                    fig, ax = plt.subplots(figsize=(10, 6))
                    cat_counts.plot(kind='barh', ax=ax, color='#667eea')
                    ax.set_xlabel('Count')
                    ax.set_title('Resumes by Category')
                    st.pyplot(fig)
                
                with col2:
                    st.subheader("💼 Skill Distribution")
                    all_skills = []
                    for skills in df['skills']:
                        all_skills.extend(skills)
                    
                    if all_skills:
                        skill_counts = pd.Series(all_skills).value_counts().head(15)
                        fig, ax = plt.subplots(figsize=(10, 6))
                        skill_counts.plot(kind='barh', ax=ax, color='#764ba2')
                        ax.set_xlabel('Frequency')
                        ax.set_title('Top 15 Skills in Pool')
                        st.pyplot(fig)
                
                st.divider()
                st.subheader("🎯 Job Requirements Analysis")
                
                clean_job_desc = preprocess_text(job_description_input)
                job_skills = extract_skills(clean_job_desc)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    create_metric_card("Required Skills", str(len(job_skills)))
                
                with col2:
                    candidates_with_any_skill = sum([
                        any(skill in resume_skills for skill in job_skills)
                        for resume_skills in df['skills']
                    ])
                    create_metric_card("Candidates with Match", str(candidates_with_any_skill), "#4CAF50")
                
                with col3:
                    match_percent = (candidates_with_any_skill / len(df) * 100) if len(df) > 0 else 0
                    create_metric_card("Match Rate", f"{match_percent:.1f}%", "#FF9800")
                
                with col4:
                    skills_in_pool = len(set(all_skills))
                    create_metric_card("Total Skills in Pool", str(skills_in_pool), "#2196F3")
                
                st.divider()
                
                st.subheader("📈 Skill Matching Distribution")
                df['skill_match_percentage'] = df['skills'].apply(
                    lambda x: calculate_skill_match_percentage(x, job_skills)
                )
                
                fig, ax = plt.subplots(figsize=(12, 5))
                ax.hist(df['skill_match_percentage'], bins=20, color='#667eea', alpha=0.7, edgecolor='black')
                ax.axvline(df['skill_match_percentage'].mean(), color='red', linestyle='--', linewidth=2, label=f"Mean: {df['skill_match_percentage'].mean():.1f}%")
                ax.axvline(df['skill_match_percentage'].median(), color='green', linestyle='--', linewidth=2, label=f"Median: {df['skill_match_percentage'].median():.1f}%")
                ax.set_xlabel('Skill Match Percentage')
                ax.set_ylabel('Number of Candidates')
                ax.set_title('Distribution of Skill Matching %')
                ax.legend()
                st.pyplot(fig)
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        else:
            st.info("👉 Run analysis from Rankings tab first")
    
    with tab3:
        st.markdown("## ⚖️ Model Comparison")
        
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
                            'Candidates': len(ranked_df),
                            'Avg Skill Match %': ranked_df['skill_match_percentage'].mean()
                        })
                
                if comparison_data:
                    comp_df = pd.DataFrame(comparison_data)
                    st.dataframe(comp_df, use_container_width=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig, ax = plt.subplots(figsize=(8, 5))
                        ax.bar(comp_df['Model'], comp_df['Avg Score'], color='#667eea')
                        ax.set_ylabel('Average Score')
                        ax.set_title('Average Score by Model')
                        ax.tick_params(axis='x', rotation=45)
                        st.pyplot(fig)
                    
                    with col2:
                        fig, ax = plt.subplots(figsize=(8, 5))
                        ax.bar(comp_df['Model'], comp_df['Avg Skill Match %'], color='#764ba2')
                        ax.set_ylabel('Average Skill Match %')
                        ax.set_title('Avg Skill Matching % by Model')
                        ax.tick_params(axis='x', rotation=45)
                        st.pyplot(fig)
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        else:
            st.info("👉 Run multiple models in Rankings tab to compare")
    
    with tab4:
        st.markdown("## 📋 Detailed Candidate Review")
        
        if st.session_state.analysis_complete and st.session_state.rankings:
            try:
                # Use the best ranking model
                best_model = list(st.session_state.rankings.keys())[0]
                ranked_df = st.session_state.rankings[best_model].copy()
                
                if filter_categories:
                    ranked_df = ranked_df[ranked_df['category'].isin(filter_categories)]
                
                df_with_skills = st.session_state.df_resumes.copy()
                df_with_skills['cleaned_text'] = df_with_skills['resume_text'].apply(preprocess_text)
                df_with_skills['skills'] = df_with_skills['cleaned_text'].apply(extract_skills)
                
                job_skills = st.session_state.job_skills_extracted
                
                st.info(f"Showing top {min(results_k, len(ranked_df))} candidates from {best_model}")
                
                for idx, (_, candidate_row) in enumerate(ranked_df.head(results_k).iterrows(), 1):
                    st.markdown(f"### Candidate #{idx}")
                    create_detailed_candidate_card(idx, candidate_row, job_skills, df_with_skills)
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        else:
            st.info("👉 Run analysis from Rankings tab first")
    
    with tab5:
        st.markdown("## 📥 Export Results")
        
        if st.session_state.analysis_complete and st.session_state.rankings:
            try:
                all_rankings = []
                for model_name, ranked_df in st.session_state.rankings.items():
                    score_columns = [col for col in ranked_df.columns if 'score' in col.lower()]
                    if score_columns:
                        score_col = score_columns[0]
                        export_df = ranked_df[['filename', 'category', score_col, 'skill_match_percentage', 'matched_skills']].copy()
                        export_df['model'] = model_name
                        export_df.columns = ['Candidate', 'Category', 'Model Score', 'Skill Match %', 'Skills Matched', 'Model']
                        all_rankings.append(export_df)
                
                if all_rankings:
                    export_data = pd.concat(all_rankings, ignore_index=True)
                    
                    csv_data = export_to_csv(export_data)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv_data,
                        file_name=f"resume_rankings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                    
                    try:
                        excel_data = export_to_excel(export_data)
                        st.download_button(
                            label="📥 Download Excel",
                            data=excel_data,
                            file_name=f"resume_rankings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    except Exception as e:
                        logger.warning(f"Excel export unavailable: {e}")
                    
                    st.divider()
                    st.subheader("Preview")
                    st.dataframe(export_data.head(20), use_container_width=True)
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        else:
            st.info("👉 Process candidates first")


st.markdown("---")
st.markdown("""
<div class='footer'>
    <h4>✨ Resume Screening Pro v4.1</h4>
    <p style='margin: 0.5rem 0;'>🎯 Advanced AI-Powered Candidate Ranking & Skill Matching</p>
    <p style='margin: 0.5rem 0; font-size: 0.85rem;'>
        Built with ❤️ | Streamlit Cloud Ready | Privacy First 🔒
    </p>
    <p style='margin-top: 1rem; font-size: 0.8rem; color: #8b92d6;'>
        © 2024-2026 Resume Screening Pro | All Rights Reserved
    </p>
</div>
""", unsafe_allow_html=True)
