# SecuRizz Deployment Guide

This guide will help you deploy SecuRizz to Solana devnet and configure all services.

## Prerequisites

### 1. Install Solana CLI

**Windows (PowerShell):**
```powershell
# Download and install Solana CLI
Invoke-WebRequest -Uri "https://github.com/solana-labs/solana/releases/download/v1.17.0/solana-install-init-x86_64-pc-windows-msvc.exe" -OutFile "solana-install-init.exe"
.\solana-install-init.exe v1.17.0
```

**Alternative (using winget):**
```powershell
winget install SolanaLabs.SolanaCLI
```

### 2. Install Anchor Framework

**Using npm:**
```bash
npm install -g @coral-xyz/anchor-cli
```

**Or using cargo:**
```bash
cargo install --git https://github.com/coral-xyz/anchor avm --locked --force
avm install latest
avm use latest
```

### 3. Install Rust (if not already installed)

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Or on Windows, download from: https://rustup.rs/
```

## Configuration Steps

### 1. Set up Solana CLI

```bash
# Configure for devnet
solana config set --url https://api.devnet.solana.com

# Create a new keypair (if you don't have one)
solana-keygen new --outfile ~/.config/solana/id.json

# Check your balance
solana balance

# Request airdrop for devnet SOL
solana airdrop 2
```

### 2. Configure Environment Variables

Copy the example files and fill in your values:

```bash
# Root directory
cp env.example .env

# Backend API
cp backend-api/env.example backend-api/.env

# Oracle Service
cp oracle-service/env.example oracle-service/.env

# Frontend
cp frontend/env.example frontend/.env.local
```

### 3. Deploy Solana Program

```bash
# Navigate to contract directory
cd solana-contract

# Build the program
anchor build

# Deploy to devnet
anchor deploy --provider.cluster devnet

# Note the program ID from the output
```

### 4. Update Program ID

After deployment, update the program ID in these files:
- `solana-contract/Anchor.toml`
- `backend-api/.env`
- `oracle-service/.env`
- `frontend/.env.local`

### 5. Set up Pinata IPFS

1. Go to [Pinata](https://pinata.cloud)
2. Create an account
3. Get your API key and secret
4. Update `PINATA_API_KEY` and `PINATA_SECRET_KEY` in `.env` files

### 6. Configure Switchboard Oracle

1. Go to [Switchboard](https://switchboard.xyz)
2. Create a new oracle
3. Get your oracle key
4. Update `SWITCHBOARD_ORACLE_KEY` in `.env` files

## Starting Services

### 1. Start Backend API

```bash
cd backend-api
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. Start Oracle Service

```bash
cd oracle-service
npm install
npm run dev
```

### 3. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

## Verification

1. **Backend API**: Visit http://localhost:8000/docs
2. **Frontend**: Visit http://localhost:3000
3. **Solana Program**: Check on Solana Explorer using your program ID

## Troubleshooting

### Common Issues:

1. **"solana not found"**: Make sure Solana CLI is installed and in PATH
2. **"anchor not found"**: Install Anchor CLI globally
3. **"Insufficient funds"**: Request airdrop with `solana airdrop 2`
4. **"Program ID not found"**: Make sure you've deployed and updated the ID

### Getting Help:

- Solana Docs: https://docs.solana.com
- Anchor Docs: https://www.anchor-lang.com
- Switchboard Docs: https://docs.switchboard.xyz
