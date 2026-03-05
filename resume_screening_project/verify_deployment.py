#!/usr/bin/env python3
"""
Streamlit Cloud Deployment Helper
Verifies all requirements for Streamlit Cloud deployment
"""
import os
import sys
from pathlib import Path

def check_deployment():
    """Check if app is ready for Streamlit Cloud"""
    
    project_root = Path(r'c:\Users\hp\Desktop\NLPpro\resume_screening_project')
    os.chdir(project_root)
    
    print("[*] Checking Streamlit Cloud Deployment Requirements")
    print("=" * 60)
    
    checks = {
        "app_pro.py at root": project_root / "app_pro.py",
        "requirements.txt": project_root / "requirements.txt",
        ".streamlit/config.toml": project_root / ".streamlit" / "config.toml",
        "src/ directory": project_root / "src",
        "data/resumes/ directory": project_root / "data" / "resumes",
    }
    
    all_good = True
    for check_name, path in checks.items():
        exists = path.exists()
        status = "[+]" if exists else "[!]"
        print(f"{status} {check_name}: {path.name}")
        if not exists:
            all_good = False
    
    print()
    print("=" * 60)
    print("[*] Streamlit Cloud Settings:")
    print()
    print("  Repository: https://github.com/gaurav2302221-cell/NLP-G1")
    print("  Branch:     main")
    print("  Main file:  app_pro.py")
    print()
    print("=" * 60)
    
    if all_good:
        print("[+] Everything looks good!")
        print("[+] Your app is ready for Streamlit Cloud deployment")
        return True
    else:
        print("[!] Some files are missing")
        print("[!] Check FIX_STREAMLIT_CLOUD.md for details")
        return False

if __name__ == "__main__":
    success = check_deployment()
    sys.exit(0 if success else 1)
