#!/bin/bash

# SecuRizz Setup Script
echo "🚀 Setting up SecuRizz - Smart Contract Vulnerability Auditor"

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Please run this script from the SecuRizz root directory"
    exit 1
fi

echo "📁 Creating necessary directories..."
mkdir -p ml-engine/models
mkdir -p backend-api/logs
mkdir -p datasets/raw
mkdir -p datasets/processed

echo "🐍 Setting up ML Engine..."
cd ml-engine
if [ ! -d ".venv" ]; then
    python -m venv .venv
fi
source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate
pip install -r requirements.txt
cd ..

echo "🔧 Setting up Backend API..."
cd backend-api
if [ ! -d ".venv" ]; then
    python -m venv .venv
fi
source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate
pip install -r requirements.txt
cd ..

echo "📦 Setting up Oracle Service..."
cd oracle-service
npm install
cd ..

echo "🌐 Setting up Frontend..."
cd frontend
npm install
cd ..

echo "📊 Generating mock dataset..."
python scripts/aggregate_datasets.py

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Copy .env.example files to .env in each service directory"
echo "2. Fill in your API keys and configuration"
echo "3. Deploy Solana program to devnet"
echo "4. Update program IDs in configuration files"
echo "5. Start services:"
echo "   - Backend: cd backend-api && uvicorn app.main:app --reload"
echo "   - Oracle: cd oracle-service && npm run dev"
echo "   - Frontend: cd frontend && npm run dev"
echo ""
echo "🎉 Happy auditing!"
