#!/usr/bin/env python3
"""
Supabase Setup Script
=====================

Script to set up Supabase integration environment.

Usage:
    python setup_supabase.py
"""

import os
import subprocess
import sys
from pathlib import Path


def install_requirements():
    """Install required packages"""
    print("📦 Installing Supabase requirements...")
    
    try:
        # Install from requirements file
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements_supabase.txt"
        ])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False


def create_env_file():
    """Create .env file from example"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("⚠️  .env file already exists")
        return True
    
    if not env_example.exists():
        print("❌ .env.example file not found")
        return False
    
    try:
        # Create .env file
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ .env file created from .env.example")
        print("📝 Please edit .env file with your Supabase credentials")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False


def test_supabase_connection():
    """Test Supabase connection"""
    print("🔍 Testing Supabase connection...")
    
    try:
        # Import and test
        from supabase_config import SupabaseConfig
        from supabase_client import SupabaseClient
        
        config = SupabaseConfig.from_env()
        client = SupabaseClient(config)
        
        print("✅ Supabase client created successfully")
        print("📝 Please run the upload script to test database connection")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("📦 Please install requirements first")
        return False
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("📝 Please check your .env file")
        return False


def main():
    """Main setup function"""
    print("🚀 Supabase Integration Setup")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("supabase_config.py").exists():
        print("❌ Please run this script from the project root directory")
        return 1
    
    # Install requirements
    if not install_requirements():
        return 1
    
    # Create .env file
    if not create_env_file():
        return 1
    
    # Test connection
    if not test_supabase_connection():
        return 1
    
    print("=" * 40)
    print("✅ Supabase setup completed!")
    print()
    print("📋 Next steps:")
    print("1. Edit .env file with your Supabase credentials")
    print("2. Run the SQL schema in Supabase SQL Editor:")
    print("   cat supabase_schema.sql")
    print("3. Test connection:")
    print("   python upload_to_supabase.py --test-connection")
    print("4. Upload data:")
    print("   python upload_to_supabase.py --input-dir output/2025-10-20")
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
