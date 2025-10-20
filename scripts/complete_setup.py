#!/usr/bin/env python3
"""
SecuRizz Complete Setup Script

This script performs a complete setup of the SecuRizz project including:
- Environment file creation
- Dependency installation
- Database initialization
- Configuration validation

Usage:
    python scripts/complete_setup.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, cwd=None, shell=True):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=shell, cwd=cwd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {command}")
            return True
        else:
            print(f"❌ {command}")
            print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {command}")
        print(f"   Exception: {e}")
        return False

def check_prerequisites():
    """Check if required tools are installed"""
    print("🔍 Checking prerequisites...")
    
    tools = {
        'python': 'python --version',
        'node': 'node --version',
        'npm': 'npm --version'
    }
    
    missing_tools = []
    
    for tool, command in tools.items():
        if not run_command(command):
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"\n❌ Missing tools: {', '.join(missing_tools)}")
        print("Please install the missing tools and run this script again.")
        return False
    
    print("✅ All prerequisites found")
    return True

def setup_environment_files():
    """Set up environment files"""
    print("\n📝 Setting up environment files...")
    
    # Copy example files to .env files
    env_files = [
        ('env.example', '.env'),
        ('backend-api/env.example', 'backend-api/.env'),
        ('oracle-service/env.example', 'oracle-service/.env'),
        ('frontend/env.example', 'frontend/.env.local')
    ]
    
    for src, dst in env_files:
        if Path(src).exists():
            shutil.copy2(src, dst)
            print(f"✅ Created {dst}")
        else:
            print(f"⚠️  Source file not found: {src}")

def setup_python_services():
    """Set up Python services (ML Engine and Backend API)"""
    print("\n🐍 Setting up Python services...")
    
    # ML Engine setup
    print("Setting up ML Engine...")
    ml_commands = [
        'python -m venv .venv',
        '.venv\\Scripts\\python.exe -m pip install --upgrade pip',
        '.venv\\Scripts\\python.exe -m pip install -r requirements.txt'
    ]
    
    for command in ml_commands:
        if not run_command(command, cwd='ml-engine'):
            print(f"⚠️  ML Engine setup had issues with: {command}")
    
    # Backend API setup
    print("Setting up Backend API...")
    backend_commands = [
        'python -m venv .venv',
        '.venv\\Scripts\\python.exe -m pip install --upgrade pip',
        '.venv\\Scripts\\python.exe -m pip install -r requirements.txt',
        '.venv\\Scripts\\python.exe -c "from app.database import create_tables; create_tables(); print(\'Database initialized\')"'
    ]
    
    for command in backend_commands:
        if not run_command(command, cwd='backend-api'):
            print(f"⚠️  Backend API setup had issues with: {command}")

def setup_node_services():
    """Set up Node.js services (Frontend and Oracle)"""
    print("\n📦 Setting up Node.js services...")
    
    # Frontend setup
    print("Setting up Frontend...")
    if not run_command('npm install', cwd='frontend'):
        print("⚠️  Frontend setup had issues")
    
    # Oracle setup
    print("Setting up Oracle Service...")
    if not run_command('npm install', cwd='oracle-service'):
        print("⚠️  Oracle Service setup had issues")

def generate_mock_data():
    """Generate mock dataset for testing"""
    print("\n📊 Generating mock dataset...")
    
    if not run_command('python scripts/aggregate_datasets.py'):
        print("⚠️  Mock dataset generation had issues")

def create_startup_scripts():
    """Create startup scripts for different platforms"""
    print("\n🚀 Creating startup scripts...")
    
    # Windows batch file
    windows_script = """@echo off
echo Starting SecuRizz Services...

echo Starting Backend API...
cd backend-api
start "Backend API" cmd /k ".venv\\Scripts\\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak > nul

echo Starting Oracle Service...
cd ..\\oracle-service
start "Oracle Service" cmd /k "npm run dev"

timeout /t 3 /nobreak > nul

echo Starting Frontend...
cd ..\\frontend
start "Frontend" cmd /k "npm run dev"

echo All services started!
echo Backend API: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs

pause
"""
    
    with open('start_services.bat', 'w') as f:
        f.write(windows_script)
    
    print("✅ Created start_services.bat")

def main():
    print("🚀 SecuRizz Complete Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Set up environment files
    setup_environment_files()
    
    # Set up Python services
    setup_python_services()
    
    # Set up Node.js services
    setup_node_services()
    
    # Generate mock data
    generate_mock_data()
    
    # Create startup scripts
    create_startup_scripts()
    
    print("\n" + "=" * 50)
    print("🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("1. Update .env files with your API keys:")
    print("   - Pinata API keys for IPFS")
    print("   - Solana program ID (after deployment)")
    print("   - Switchboard oracle credentials")
    print("\n2. Deploy Solana program:")
    print("   - Follow DEPLOYMENT.md instructions")
    print("   - Run: python scripts/update_program_id.py <PROGRAM_ID>")
    print("\n3. Start services:")
    print("   - Windows: double-click start_services.bat")
    print("   - Or manually start each service")
    print("\n4. Test the application:")
    print("   - Frontend: http://localhost:3000")
    print("   - API Docs: http://localhost:8000/docs")
    print("\n🎯 Happy auditing!")

if __name__ == "__main__":
    main()
