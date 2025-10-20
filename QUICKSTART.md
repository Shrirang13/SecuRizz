# SecuRizz Quick Start Guide

Get SecuRizz up and running in 5 minutes! 🚀

## Prerequisites

- Python 3.8+
- Node.js 18+
- Git

## One-Command Setup

```bash
# Clone and setup everything
git clone https://github.com/Shrirang13/SecuRizz.git
cd SecuRizz
python scripts/complete_setup.py
```

## Manual Setup (if needed)

### 1. Install Dependencies

```bash
# Python services
cd ml-engine && python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt
cd ../backend-api && python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt

# Node.js services
cd ../frontend && npm install
cd ../oracle-service && npm install
```

### 2. Configure Environment

```bash
# Copy environment files
cp env.example .env
cp backend-api/env.example backend-api/.env
cp oracle-service/env.example oracle-service/.env
cp frontend/env.example frontend/.env.local
```

### 3. Start Services

**Option A: Use the batch file (Windows)**
```bash
# Double-click start_services.bat
```

**Option B: Start manually**
```bash
# Terminal 1 - Backend API
cd backend-api
.venv\Scripts\activate
uvicorn app.main:app --reload

# Terminal 2 - Oracle Service
cd oracle-service
npm run dev

# Terminal 3 - Frontend
cd frontend
npm run dev
```

## Test the Application

1. **Frontend**: http://localhost:3000
2. **API Docs**: http://localhost:8000/docs
3. **Health Check**: http://localhost:8000/health

## Deploy to Solana (Optional)

For full functionality with on-chain proofs:

1. **Install Solana CLI**:
   ```bash
   # Windows
   winget install SolanaLabs.SolanaCLI
   ```

2. **Install Anchor**:
   ```bash
   npm install -g @coral-xyz/anchor-cli
   ```

3. **Deploy Program**:
   ```bash
   cd solana-contract
   anchor build
   anchor deploy --provider.cluster devnet
   ```

4. **Update Program ID**:
   ```bash
   python scripts/update_program_id.py <YOUR_PROGRAM_ID>
   ```

## Configure External Services

### Pinata IPFS (for report storage)
1. Go to [pinata.cloud](https://pinata.cloud)
2. Create account and get API keys
3. Update `PINATA_API_KEY` and `PINATA_SECRET_KEY` in `.env` files

### Switchboard Oracle (for blockchain integration)
1. Go to [console.switchboard.xyz](https://console.switchboard.xyz)
2. Create oracle on devnet
3. Update `SWITCHBOARD_ORACLE_KEY` in `.env` files

## Troubleshooting

### Common Issues

**"python not found"**
```bash
# Install Python from python.org or use winget
winget install Python.Python.3.11
```

**"npm not found"**
```bash
# Install Node.js from nodejs.org or use winget
winget install OpenJS.NodeJS
```

**"Port already in use"**
```bash
# Kill processes on ports 3000 and 8000
netstat -ano | findstr :3000
netstat -ano | findstr :8000
# Then kill the PIDs
```

**"Module not found"**
```bash
# Reinstall dependencies
cd frontend && npm install
cd ../oracle-service && npm install
```

### Getting Help

- 📖 **Full Documentation**: See README.md
- 🚀 **Deployment Guide**: See DEPLOYMENT.md
- 🐛 **Issues**: Create an issue on GitHub
- 💬 **Discord**: Join our community

## What's Next?

1. **Upload a contract** and see AI analysis
2. **View vulnerability reports** with risk scores
3. **Deploy to Solana** for on-chain proofs
4. **Integrate with your project** using our API

## Features Available

✅ **AI Vulnerability Detection** - 15+ vulnerability types  
✅ **Real-time Analysis** - Results in under 30 seconds  
✅ **IPFS Storage** - Decentralized report storage  
✅ **REST API** - Easy integration  
✅ **Web Dashboard** - User-friendly interface  
✅ **Mock Dataset** - Ready for testing  

## Production Deployment

For production deployment, see DEPLOYMENT.md for detailed instructions including:
- Solana program deployment
- Environment configuration
- Security considerations
- Performance optimization

---

**Happy Auditing!** 🔒✨
