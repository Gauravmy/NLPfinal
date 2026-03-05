# Streamlit Cloud Application Configuration

This file helps Streamlit Cloud properly deploy the Resume Screening Pro application.

## Deployment Details

**Repository**: https://github.com/gaurav2302221-cell/NLP-G1  
**Branch**: main  
**App File**: src/app_pro.py  
**Python Version**: 3.8+  

## To Deploy on Streamlit Cloud:

1. Go to https://streamlit.io/cloud
2. Click "New app"
3. Enter:
   - Repository: gaurav2302221-cell/NLP-G1
   - Branch: main
   - Main file path: src/app_pro.py
4. Click "Deploy"

## Configuration Files

- `.streamlit/config.toml` - Streamlit theme and settings
- `requirements.txt` - All Python dependencies
- `src/app_pro.py` - Main application entry point
- `.gitignore` - Git ignore rules

## Troubleshooting

If you see "You do not have access to this app":

1. **Check Repository is Public**
   - Go to https://github.com/gaurav2302221-cell/NLP-G1/settings
   - Verify it's set to "Public"

2. **Verify Python Dependencies**
   - All dependencies are in `requirements.txt`
   - Run: `pip install -r requirements.txt`

3. **Check App File Path**
   - App file must be: `src/app_pro.py`
   - Path is relative to repository root

4. **Clear Streamlit Cache**
   - Delete `.streamlit/cache_dir/`
   - Redeploy app

5. **Check Branch Commits**
   - Ensure changes are pushed to `main` branch
   - Verify on GitHub that files are visible

## Manual Deployment Test

To test locally before Streamlit Cloud:

```bash
cd resume_screening_project
streamlit run src/app_pro.py
```

This should open at: `http://localhost:8501`
