#!/usr/bin/env python3
"""
Zizie Build Check Script
Verifies environment and dependencies
"""
import os
import sys

def print_status(name: str, status: str, emoji: str = "❌"):
    print(f"{emoji} {name}: {status}")

def main():
    print("=" * 50)
    print("ZIZIE BUILD CHECK")
    print("=" * 50)
    
    # Check Python
    print_status("Python", f"{sys.version.split()[0]}", "✅")
    
    # Check critical files
    files = [
        "main.py",
        "requirements.txt",
        "app/api/v1/auth.py",
        "app/api/v1/voice.py",
        "app/core/config.py",
    ]
    
    for f in files:
        exists = os.path.exists(f"/workspace/project/zizie-backend/{f}")
        print_status(f"File: {f}", "Found" if exists else "Missing", "✅" if exists else "❌")
    
    print()
    print("=" * 50)
    print("REQUIRED ENVIRONMENT VARIABLES")
    print("=" * 50)
    
    required = [
        "POSTGRES_HOST",
        "POSTGRES_USER", 
        "POSTGRES_PASSWORD",
        "OPENAI_API_KEY",
        "PICOVOICE_API_KEY",
        "SECRET_KEY",
    ]
    
    missing = []
    for var in required:
        value = os.getenv(var, "")
        if value and value not in ["", "change-me", "...", "sk-..."]:
            print_status(var, "✓ Set", "✅")
        else:
            print_status(var, "NEEDS TO BE SET", "⚠️")
            missing.append(var)
    
    print()
    if missing:
        print("=" * 50)
        print("NEXT STeps")
        print("=" * 50)
        print(f"Missing variables: {', '.join(missing)}")
        print("\n1. Set environment variables in .env")
        print("2. Start PostgreSQL database")
        print("3. Run: pip install -r requirements.txt")
        print("4. Run: uvicorn main:app --reload")
        return 1
    else:
        print_status("Environment", "READY TO BUILD", "✅")
        return 0

if __name__ == "__main__":
    sys.exit(main())