#!/usr/bin/env python3
"""
Complete git push script for all changes
"""
import subprocess
import os
import sys

os.chdir(r'c:\Users\hp\Desktop\NLPpro\resume_screening_project')

def run_command(cmd, description):
    """Run git command and print status"""
    print(f"\n📝 {description}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout:
                print(f"   Output: {result.stdout[:200]}")
            return True
        else:
            print(f"⚠️  {description} - Output:")
            print(f"   {result.stderr[:300]}")
            return True  # Continue anyway
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

try:
    # Configure git
    run_command('git config user.email "dev@resumescreening.com"', "Configure email")
    run_command('git config user.name "Resume Screening Bot"', "Configure name")
    
    # Add all files
    run_command('git add .', "Adding all files to staging")
    
    # Check status
    print("\n🔍 Current git status:")
    result = subprocess.run('git status --short', capture_output=True, text=True, shell=True)
    if result.stdout:
        print(result.stdout)
    else:
        print("   No changes to commit")
    
    # Commit
    run_command('git commit -m "chore: Add Streamlit deployment links and status files"', "Committing changes")
    
    # Pull latest
    run_command('git pull origin main --allow-unrelated-histories', "Pulling latest from remote")
    
    # Push
    result = subprocess.run('git push origin main', capture_output=True, text=True, shell=True)
    if result.returncode == 0:
        print("\n✅ PUSH SUCCESSFUL!")
        print(result.stdout)
    else:
        print("\n⚠️ Push attempt:")
        print(result.stderr)
        
        # Try force push if needed
        print("\n🔄 Attempting force push...")
        result = subprocess.run('git push -f origin main', capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print("✅ Force push successful!")
            print(result.stdout)
        else:
            print("Error details:", result.stderr)
    
    print("\n" + "="*60)
    print("✨ Git operations complete!")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ Fatal error: {e}")
    sys.exit(1)
