#!/usr/bin/env python3
"""
Git commit script for README updates
"""
import subprocess
import os

os.chdir(r'c:\Users\hp\Desktop\NLPpro\resume_screening_project')

try:
    # Configure git
    subprocess.run(['git', 'config', 'user.email', 'dev@resumescreening.com'], check=True)
    subprocess.run(['git', 'config', 'user.name', 'Resume Screening Bot'], check=True)
    
    # Add README
    subprocess.run(['git', 'add', 'README.md'], check=True)
    
    # Commit
    subprocess.run(['git', 'commit', '-m', 'docs: Add Streamlit Cloud deployment links and live app URL'], check=True)
    
    # Push to main
    subprocess.run(['git', 'push', 'origin', 'main'], check=True)
    
    print("✅ Successfully committed and pushed changes!")
    
except subprocess.CalledProcessError as e:
    print(f"❌ Git operation failed: {e}")
    exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
