#!/usr/bin/env python3
"""
Simple runner script for dummy data insertion
"""

import subprocess
import sys
import os

def main():
    """Run the dummy data insertion script"""
    script_path = os.path.join(os.path.dirname(__file__), "insert_dummy_data.py")
    
    print("Running dummy data insertion script...")
    print("Make sure your database is running and environment variables are set!")
    print("-" * 60)
    
    try:
        result = subprocess.run([sys.executable, script_path], check=True)
        print("-" * 60)
        print("✅ Dummy data insertion completed successfully!")
        print("\nYou can now test your APIs with the following test users:")
        print("📧 john.doe@example.com (password: password123)")
        print("📧 jane.smith@example.com (password: password123)")
        print("📧 mike.johnson@example.com (password: password123)")
        print("📧 sarah.wilson@example.com (password: password123)")
        print("📧 david.brown@example.com (password: password123)")
        print("📧 lisa.davis@example.com (password: password123)")
        print("📧 tom.anderson@example.com (password: password123)")
        print("📧 emma.taylor@example.com (password: password123)")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running dummy data script: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"❌ Could not find insert_dummy_data.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
