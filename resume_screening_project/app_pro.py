"""
Resume Screening System - Streamlit Web Application (Enhanced UI/UX)

Professional dashboard for automated resume screening and candidate ranking
with advanced NLP techniques and beautiful, intuitive interface.

Author: AI/ML Engineering Team
Version: 2.0.0 (Production)
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO, StringIO
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import custom modules
from src.resume_parser import parse_resume
from src.text_preprocessing import preprocess_text
from src.skill_extractor import extract_skills, extract_job_skills
from src.job_parser import process_job_description
from src.similarity_model import compute_similarity, initialize_bert_model
from src.ranking_engine import rank_candidates, get_top_candidates
from src.model_comparison import (
    rank_by_tfidf, rank_by_bert, rank_by_hybrid, rank_by_deep_ensemble
)
from src.evaluation import (
    precision_at_k_multi, recall_at_k_multi, mean_average_precision_multi
)

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Resume Screening Pro",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com',
        'Report a bug': 'https://github.com',
        'About': "Resume Screening System v2.0"
    }
)

# ============================================================================
# CUSTOM STYLING
# ============================================================================

st.markdown("""
    <style>
        /* Main container */
        .main {
            padding: 2rem;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        /* Headers */
        h1 {
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
            font-size: 2.5rem;
            font-weight: 700;
        }
        
        h2 {
            color: #1f77b4;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            font-size: 1.8rem;
        }
        
        h3 {
            color: #555;
            margin-top: 1rem;
            font-size: 1.3rem;
        }
        
        /* Metric boxes */
        .metric-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        /* Cards */
        .card {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Success message */
        .success-box {
            background: #d4edda;
            color: #155724;
            padding: 1rem;
            border-radius: 5px;
            border-left: 4px solid #28a745;
            margin: 1rem 0;
        }
        
        /* Warning box */
        .warning-box {
            background: #fff3cd;
            color: #856404;
            padding: 1rem;
            border-radius: 5px;
            border-left: 4px solid #ffc107;
            margin: 1rem 0;
        }
        
        /* Button styling */
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
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
        }
        
        /* Tables */
        .dataframe {
            font-size: 0.95rem;
        }
        
        .stDataFrame {
            overflow: auto;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f8f9fa 0%, #f0f0f0 100%);
        }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# CACHE MANAGEMENT
# ============================================================================

@st.cache_resource
def load_bert_model():
    """Load BERT model once and cache it."""
    initialize_bert_model()
    return True

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_resumes_from_directory(data_path: str) -> pd.DataFrame:
    """Load resumes from directory structure."""
    try:
        data = []
        data_path = Path(data_path)
        
        if not data_path.exists():
            st.error(f"Data directory not found: {data_path}")
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
        
        if not data:
            st.warning(f"No resume files found in {data_path}")
            return pd.DataFrame()
        
        return pd.DataFrame(data)
    
    except Exception as e:
        st.error(f"Error loading resumes: {e}")
        return pd.DataFrame()

def create_metric_card(label: str, value: str, color: str = "#667eea"):
    """Create a styled metric card."""
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, {color} 0%, #764ba2 100%);
                    color: white; padding: 1.5rem; border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;">
            <h3 style="margin: 0; font-size: 0.9rem; opacity: 0.9;">{label}</h3>
            <h2 style="margin: 0.5rem 0; color: white; font-size: 2rem;">{value}</h2>
        </div>
    """, unsafe_allow_html=True)

# ============================================================================
# PAGE LAYOUT
# ============================================================================

# Header
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown("<h1>📄 Resume Screening Pro</h1>", unsafe_allow_html=True)

st.markdown("---")

# Sidebar Configuration
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    # Data Source Selection
    st.subheader("📁 Data Source")
    data_path = st.text_input(
        "Resume Data Directory",
        value="./data/resumes",
        help="Path to directory containing resume files organized by category"
    )
    
    # Load data
    if st.button("📂 Load Resumes", use_container_width=True):
        st.session_state.df_resumes = load_resumes_from_directory(data_path)
        if not st.session_state.df_resumes.empty:
            st.success(f"✓ Loaded {len(st.session_state.df_resumes)} resumes")
        else:
            st.error("Failed to load resumes")
    
    st.divider()
    
    # Job Description Input
    st.subheader("💼 Job Description")
    job_description_input = st.text_area(
        "Enter Job Requirements",
        value="",
        height=150,
        placeholder="""Senior Software Engineer
        
Required:
- Python, Machine Learning
- Deep Learning, SQL
- TensorFlow or PyTorch

Preferred:
- NLP experience
- Cloud platforms
- Docker and Kubernetes"""
    )
    
    st.divider()
    
    # Model Selection
    st.subheader("🤖 Ranking Model")
    selected_models = st.multiselect(
        "Select Models to Compare",
        options=["TF-IDF", "BERT", "Hybrid", "Deep Ensemble"],
        default=["Deep Ensemble"],
        help="Select which ranking models to use"
    )
    
    # Results K-value
    st.subheader("📊 Results")
    results_k = st.slider(
        "Top-K Candidates",
        min_value=5,
        max_value=50,
        value=10,
        step=5
    )
    
    # Category Filter
    st.subheader("🏷️ Category Filter")
    filter_categories = st.multiselect(
        "Filter by Category (leave empty for all)",
        options=[],
        help="Optionally filter results by category"
    )
    
    st.divider()
    
    # About
    st.markdown("### About This App")
    st.markdown("""
    **Resume Screening Pro v2.0**
    
    Advanced resume screening system with:
    - 4 ranking models (TF-IDF, BERT, Hybrid, Ensemble)
    - Skill extraction & matching
    - Performance evaluation
    - Result visualization
    
    Built with Streamlit, Scikit-learn, and Sentence Transformers
    """)

# ============================================================================
# MAIN CONTENT AREA
# ============================================================================

# Initialize session state
if 'df_resumes' not in st.session_state:
    st.session_state.df_resumes = pd.DataFrame()
if 'rankings' not in st.session_state:
    st.session_state.rankings = {}

# Check if data is loaded
if st.session_state.df_resumes.empty:
    st.info("👈 **Start here:** Load resumes from the left sidebar")
elif not job_description_input.strip():
    st.info("👈 **Next step:** Enter a job description in the sidebar")
else:
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["🎯 Rankings", "📊 Analysis", "🏆 Comparison", "💾 Export"]
    )
    
    # ====== TAB 1: RANKINGS ======
    with tab1:
        st.markdown("## Candidate Rankings")
        
        # Process data
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Preprocess
            status_text.text("⏳ Preprocessing resumes...")
            df = st.session_state.df_resumes.copy()
            df['cleaned_text'] = df['resume_text'].apply(preprocess_text)
            progress_bar.progress(20)
            
            # Extract skills
            status_text.text("⏳ Extracting skills...")
            df['skills'] = df['cleaned_text'].apply(extract_skills)
            progress_bar.progress(40)
            
            # Process job description
            status_text.text("⏳ Processing job description...")
            clean_job_desc = preprocess_text(job_description_input)
            job_skills = extract_job_skills(job_description_input)
            progress_bar.progress(60)
            
            # Load BERT model
            load_bert_model()
            progress_bar.progress(80)
            
            # Run rankings
            st.session_state.rankings = {}
            
            if "TF-IDF" in selected_models:
                status_text.text("⏳ Running TF-IDF ranking...")
                st.session_state.rankings['TF-IDF'] = rank_by_tfidf(df, clean_job_desc)
            
            if "BERT" in selected_models:
                status_text.text("⏳ Running BERT ranking...")
                st.session_state.rankings['BERT'] = rank_by_bert(df, clean_job_desc)
            
            if "Hybrid" in selected_models:
                status_text.text("⏳ Running Hybrid ranking...")
                st.session_state.rankings['Hybrid'] = rank_by_hybrid(df, clean_job_desc, job_skills)
            
            if "Deep Ensemble" in selected_models:
                status_text.text("⏳ Running Deep Ensemble ranking...")
                st.session_state.rankings['Deep Ensemble'] = rank_by_deep_ensemble(
                    df, clean_job_desc, job_skills
                )
            
            progress_bar.progress(100)
            status_text.empty()
            progress_bar.empty()
            
            # Display results
            st.success(f"✅ Rankings complete! Found {len(df)} resumes")
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                create_metric_card("Total Resumes", str(len(df)))
            with col2:
                create_metric_card("Categories", str(df['category'].nunique()), "#2196F3")
            with col3:
                create_metric_card("Avg Skills", f"{df['skills'].apply(len).mean():.1f}", "#4CAF50")
            with col4:
                create_metric_card("Job Skills", str(len(job_skills)), "#FF9800")
            
            st.divider()
            
            # Display rankings by model
            for model_name, ranked_df in st.session_state.rankings.items():
                st.subheader(f"🏅 {model_name} Rankings")
                
                # Get score column
                score_columns = [col for col in ranked_df.columns if 'score' in col.lower()]
                if score_columns:
                    score_col = score_columns[0]
                    
                    # Display table
                    display_df = ranked_df.head(results_k)[[
                        'filename', 'category', score_col
                    ]].copy()
                    display_df = display_df.reset_index(drop=True)
                    display_df.index = display_df.index + 1
                    display_df.index.name = 'Rank'
                    display_df.columns = ['Filename', 'Category', 'Score']
                    display_df['Score'] = display_df['Score'].apply(lambda x: f"{x:.2f}")
                    
                    st.dataframe(display_df, use_container_width=True)
        
        except Exception as e:
            st.error(f"❌ Error during processing: {str(e)}")
            logger.exception(e)
    
    # ====== TAB 2: ANALYSIS ======
    with tab2:
        st.markdown("## Detailed Analysis")
        
        if st.session_state.rankings:
            try:
                df = st.session_state.df_resumes.copy()
                df['cleaned_text'] = df['resume_text'].apply(preprocess_text)
                df['skills'] = df['cleaned_text'].apply(extract_skills)
                
                # Category distribution
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Category Distribution")
                    cat_counts = df['category'].value_counts()
                    fig, ax = plt.subplots(figsize=(10, 6))
                    cat_counts.plot(kind='barh', ax=ax, color='#667eea')
                    ax.set_xlabel('Number of Resumes')
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
                        ax.set_title('Top 15 Skills in Resumes')
                        st.pyplot(fig)
                
                # Job skills matching
                st.divider()
                st.subheader("Job Skills Analysis")
                
                clean_job_desc = preprocess_text(job_description_input)
                job_skills = extract_job_skills(job_description_input)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Required Skills", len(job_skills))
                
                with col2:
                    # Calculate how many candidates have at least 1 skill
                    candidates_with_skills = sum(1 for skills in df['skills'] if any(s in job_skills for s in skills))
                    pct = (candidates_with_skills / len(df) * 100) if len(df) > 0 else 0
                    st.metric("Candidates with Skills", f"{candidates_with_skills} ({pct:.1f}%)")
                
                with col3:
                    # Average skill overlap
                    overlaps = []
                    for skills in df['skills']:
                        overlap = len(set(skills) & job_skills)
                        overlaps.append(overlap)
                    avg_overlap = np.mean(overlaps) if overlaps else 0
                    st.metric("Avg Skill Overlap", f"{avg_overlap:.2f}")
                
                # Skill match details
                st.subheader("Top Required Skills Found")
                skill_match_data = []
                for skill in list(job_skills)[:10]:
                    count = sum(1 for skills in df['skills'] if skill in skills)
                    pct = (count / len(df) * 100) if len(df) > 0 else 0
                    skill_match_data.append({
                        'Skill': skill,
                        'Found in Resumes': f"{count} ({pct:.1f}%)"
                    })
                
                if skill_match_data:
                    st.dataframe(pd.DataFrame(skill_match_data), use_container_width=True)
            
            except Exception as e:
                st.error(f"Analysis error: {str(e)}")
        else:
            st.info("Run rankings first to see analysis")
    
    # ====== TAB 3: COMPARISON ======
    with tab3:
        st.markdown("## Model Comparison")
        
        if len(st.session_state.rankings) > 1:
            try:
                # Model performance comparison
                st.subheader("Model Performance Metrics")
                
                df = st.session_state.df_resumes.copy()
                df['cleaned_text'] = df['resume_text'].apply(preprocess_text)
                df['skills'] = df['cleaned_text'].apply(extract_skills)
                
                relevant_categories = df['category'].unique()[:2]  # Top 2 categories
                
                comparison_data = {}
                for model_name, ranked_df in st.session_state.rankings.items():
                    try:
                        comparison_data[model_name] = {
                            'Precision@10': precision_at_k_multi(ranked_df, 10, 'category', list(relevant_categories)),
                            'Recall@10': recall_at_k_multi(ranked_df, 10, 'category', list(relevant_categories)),
                            'MAP': mean_average_precision_multi(ranked_df, 'category', list(relevant_categories))
                        }
                    except:
                        pass
                
                if comparison_data:
                    comparison_df = pd.DataFrame(comparison_data).T
                    
                    # Display metrics table
                    st.dataframe(comparison_df.round(4), use_container_width=True)
                    
                    # Visualize comparison
                    st.subheader("Performance Visualization")
                    
                    fig, ax = plt.subplots(figsize=(12, 6))
                    comparison_df.plot(kind='bar', ax=ax, color=['#667eea', '#764ba2', '#f093fb'])
                    ax.set_title('Model Performance Comparison')
                    ax.set_ylabel('Score')
                    ax.set_xlabel('Model')
                    ax.legend(title='Metrics', loc='upper left')
                    plt.xticks(rotation=45)
                    st.pyplot(fig)
                else:
                    st.warning("Could not compute comparison metrics")
            
            except Exception as e:
                st.error(f"Comparison error: {str(e)}")
        else:
            st.info("Select multiple models to compare")
    
    # ====== TAB 4: EXPORT ======
    with tab4:
        st.markdown("## Export Results")
        
        if st.session_state.rankings:
            export_method = st.radio(
                "Select Export Format",
                ["CSV (Preferred)", "Excel", "JSON"],
                horizontal=True
            )
            
            export_date = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            for model_name, ranked_df in st.session_state.rankings.items():
                st.subheader(f"Export {model_name} Results")
                
                # Select columns to export
                score_col = [col for col in ranked_df.columns if 'score' in col.lower()]
                if score_col:
                    score_col = score_col[0]
                    export_cols = ['filename', 'category', score_col]
                    
                    if all(col in ranked_df.columns for col in export_cols):
                        export_df = ranked_df[export_cols].head(50).copy()
                        
                        if export_method == "CSV (Preferred)":
                            csv = export_df.to_csv(index=False)
                            st.download_button(
                                label=f"📥 Download {model_name} as CSV",
                                data=csv,
                                file_name=f"rankings_{model_name.lower().replace(' ', '_')}_{export_date}.csv",
                                mime="text/csv",
                                key=f"csv_{model_name}"
                            )
                        
                        elif export_method == "Excel":
                            buffer = BytesIO()
                            export_df.to_excel(buffer, index=False)
                            buffer.seek(0)
                            st.download_button(
                                label=f"📥 Download {model_name} as Excel",
                                data=buffer.getvalue(),
                                file_name=f"rankings_{model_name.lower().replace(' ', '_')}_{export_date}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key=f"excel_{model_name}"
                            )
                        
                        elif export_method == "JSON":
                            json_str = export_df.to_json(orient='records', indent=2)
                            st.download_button(
                                label=f"📥 Download {model_name} as JSON",
                                data=json_str,
                                file_name=f"rankings_{model_name.lower().replace(' ', '_')}_{export_date}.json",
                                mime="application/json",
                                key=f"json_{model_name}"
                            )
            
            st.divider()
            
            # Summary report
            st.subheader("Summary Report")
            summary_data = {
                'Metric': [
                    'Total Resumes Analyzed',
                    'Total Categories',
                    'Models Used',
                    'Processing Date'
                ],
                'Value': [
                    len(st.session_state.df_resumes),
                    st.session_state.df_resumes['category'].nunique(),
                    ', '.join(st.session_state.rankings.keys()),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ]
            }
            st.dataframe(pd.DataFrame(summary_data), use_container_width=True)
        
        else:
            st.info("Run rankings first to export results")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.9rem; margin-top: 2rem;">
        <p>Resume Screening Pro v2.0 | Built with ❤️ using Streamlit</p>
        <p>© 2026 All Rights Reserved</p>
    </div>
""", unsafe_allow_html=True)
