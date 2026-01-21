#!/usr/bin/env python3
"""
Pre-Deploy Checklist Script

Verifica que todo esté listo para hacer deploy a producción.
Ejecutar antes de hacer push a main:

    python scripts/pre_deploy_check.py
"""

import os
import sys
from pathlib import Path

# ANSI colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def check_file(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"{GREEN}✅{RESET} {description}")
        return True
    else:
        print(f"{RED}❌{RESET} {description}")
        print(f"   Missing: {filepath}")
        return False

def check_git_status():
    """Check if git is clean"""
    import subprocess
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            print(f"{YELLOW}⚠️{RESET}  Uncommitted changes detected")
            print("   You have uncommitted changes. Commit them before deploy:")
            print("   git add .")
            print("   git commit -m 'Ready for deploy'")
            return False
        else:
            print(f"{GREEN}✅{RESET} Git status clean")
            return True
    except FileNotFoundError:
        print(f"{YELLOW}⚠️{RESET}  Git not found (skipping check)")
        return True

def check_env_example():
    """Check if .env.example is updated"""
    env_example = Path("backend/.env.example")
    env_prod = Path("backend/.env.production.example")
    
    if not env_example.exists():
        print(f"{RED}❌{RESET} backend/.env.example missing")
        return False
    
    if not env_prod.exists():
        print(f"{RED}❌{RESET} backend/.env.production.example missing")
        return False
    
    print(f"{GREEN}✅{RESET} Environment templates present")
    return True

def main():
    print_header("🚀 PRE-DEPLOY CHECKLIST")
    
    checks = []
    
    # Check critical files
    print("\n📁 Checking critical files...")
    checks.append(check_file("backend/Dockerfile", "Backend Dockerfile"))
    checks.append(check_file("backend/requirements.txt", "Backend requirements"))
    checks.append(check_file("backend/app/main.py", "Backend main.py"))
    checks.append(check_file("frontend/package.json", "Frontend package.json"))
    checks.append(check_file("vercel.json", "Vercel configuration"))
    checks.append(check_file("railway.json", "Railway configuration"))
    checks.append(check_file("docs/DEPLOY.md", "Deploy documentation"))
    
    # Check env files
    print("\n🔐 Checking environment files...")
    checks.append(check_env_example())
    
    # Check git status
    print("\n📦 Checking git status...")
    checks.append(check_git_status())
    
    # Check if on main branch
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True
        )
        branch = result.stdout.strip()
        if branch == 'main' or branch == 'master':
            print(f"{GREEN}✅{RESET} On main branch ({branch})")
            checks.append(True)
        else:
            print(f"{YELLOW}⚠️{RESET}  Not on main branch (current: {branch})")
            print("   Deploy to production happens from 'main' branch")
            checks.append(False)
    except:
        print(f"{YELLOW}⚠️{RESET}  Could not determine branch (skipping)")
        checks.append(True)
    
    # Summary
    print_header("📊 SUMMARY")
    
    total = len(checks)
    passed = sum(checks)
    failed = total - passed
    
    print(f"Total checks: {total}")
    print(f"{GREEN}Passed: {passed}{RESET}")
    if failed > 0:
        print(f"{RED}Failed: {failed}{RESET}")
    
    if all(checks):
        print(f"\n{GREEN}{'='*60}{RESET}")
        print(f"{GREEN}✅ ALL CHECKS PASSED - READY FOR DEPLOY!{RESET}")
        print(f"{GREEN}{'='*60}{RESET}\n")
        print("Next steps:")
        print("1. Push to GitHub: git push origin main")
        print("2. Railway will auto-deploy backend")
        print("3. Vercel will auto-deploy frontend")
        print("\nOr follow the manual steps in docs/DEPLOY.md")
        return 0
    else:
        print(f"\n{RED}{'='*60}{RESET}")
        print(f"{RED}❌ SOME CHECKS FAILED - FIX ISSUES BEFORE DEPLOY{RESET}")
        print(f"{RED}{'='*60}{RESET}\n")
        print("Fix the issues above and run this script again.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
