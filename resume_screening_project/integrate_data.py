"""
Quick Data Integration Script

Run this script to integrate the Resume.csv data into your project.

Usage:
    python integrate_data.py
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_integrator import quick_integrate_data


def main():
    """Main integration execution."""
    
    # Source CSV path
    csv_path = r"c:\Users\hp\Downloads\archive (19)\Resume\Resume.csv"
    
    # Target directory
    output_dir = os.path.join(
        os.path.dirname(__file__),
        'data', 'resumes'
    )
    
    # Verify CSV exists
    if not os.path.exists(csv_path):
        print(f"ERROR: CSV file not found at {csv_path}")
        print("Please verify the path to the Resume.csv file")
        return False
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Run integration
    try:
        count, stats = quick_integrate_data(csv_path, output_dir)
        
        if count > 0:
            print("\n" + "="*70)
            print("DATA INTEGRATION SUCCESS!")
            print("="*70)
            print(f"\nProcessed Resumes: {count}")
            print(f"Total Categories: {stats.get('categories', 0)}")
            print(f"\nResumes by Category:")
            for category, count_cat in stats.get('category_distribution', {}).items():
                print(f"  • {category}: {count_cat} resumes")
            
            print(f"\nResume Statistics:")
            print(f"  • Average length: {stats.get('avg_resume_length', 0):.0f} characters")
            print(f"  • Max length: {stats.get('max_resume_length', 0):.0f} characters")
            print(f"  • Min length: {stats.get('min_resume_length', 0):.0f} characters")
            
            print(f"\nOutput Directory: {output_dir}")
            print("="*70 + "\n")
            
            return True
        else:
            print("ERROR: No resumes were processed")
            return False
            
    except Exception as e:
        print(f"ERROR during integration: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
