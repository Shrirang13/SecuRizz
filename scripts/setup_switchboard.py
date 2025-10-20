#!/usr/bin/env python3
"""
SecuRizz Switchboard Oracle Setup Script

This script helps set up Switchboard oracle configuration for SecuRizz.

Usage:
    python scripts/setup_switchboard.py
"""

import json
import os
import sys
from pathlib import Path

def create_switchboard_config():
    """Create Switchboard oracle configuration"""
    
    print("🔧 Setting up Switchboard Oracle Configuration")
    print("=" * 50)
    
    # Switchboard configuration template
    switchboard_config = {
        "oracle": {
            "name": "SecuRizz Oracle",
            "description": "Oracle service for SecuRizz smart contract vulnerability auditor",
            "cluster": "devnet",
            "queue": "devnet-default",
            "authority": "ReplaceWithOracleAuthority",
            "oracle_key": "ReplaceWithOracleKey"
        },
        "feeds": [
            {
                "name": "SecuRizz Audit Feed",
                "description": "Feed for audit report verification",
                "type": "custom",
                "update_interval": 30,
                "variance_threshold": 0.1
            }
        ],
        "instructions": {
            "submit_proof": {
                "description": "Submit audit proof to Solana program",
                "required_accounts": ["audit_proof", "oracle", "system_program"],
                "data_fields": ["contract_hash", "report_hash", "ipfs_cid", "risk_score"]
            },
            "update_verification": {
                "description": "Update verification status",
                "required_accounts": ["audit_proof", "authority"],
                "data_fields": ["verified"]
            }
        }
    }
    
    # Save configuration
    config_path = Path("oracle-service/switchboard_config.json")
    with open(config_path, 'w') as f:
        json.dump(switchboard_config, f, indent=2)
    
    print(f"✅ Created Switchboard config: {config_path}")
    
    # Create oracle setup instructions
    instructions = """
# Switchboard Oracle Setup Instructions

## 1. Create Switchboard Account

1. Go to [Switchboard Console](https://console.switchboard.xyz)
2. Connect your Solana wallet
3. Switch to Devnet
4. Create a new Oracle

## 2. Get Oracle Credentials

After creating the oracle, you'll get:
- Oracle Authority (your wallet public key)
- Oracle Key (generated oracle public key)
- Queue ID (usually 'devnet-default')

## 3. Update Environment Variables

Update your `.env` files with:

```bash
# Oracle Service .env
SWITCHBOARD_QUEUE=devnet-default
SWITCHBOARD_ORACLE_KEY=your_oracle_key_here
SOLANA_WALLET_PATH=~/.config/solana/id.json
```

## 4. Fund Oracle Account

```bash
# Fund your oracle wallet
solana airdrop 2

# Check balance
solana balance
```

## 5. Test Oracle Connection

```bash
cd oracle-service
npm run dev
```

## 6. Verify on Switchboard Console

1. Go to your oracle dashboard
2. Check that it's showing as "Active"
3. Monitor for incoming requests

## Troubleshooting

- **"Oracle not found"**: Make sure you're on the correct cluster (devnet)
- **"Insufficient funds"**: Airdrop more SOL to your oracle wallet
- **"Queue not found"**: Use 'devnet-default' as the queue ID
- **"Invalid authority"**: Make sure your wallet is the oracle authority

## Support

- Switchboard Docs: https://docs.switchboard.xyz
- Discord: https://discord.gg/switchboardxyz
- GitHub: https://github.com/switchboard-xyz
"""
    
    instructions_path = Path("oracle-service/SWITCHBOARD_SETUP.md")
    with open(instructions_path, 'w') as f:
        f.write(instructions)
    
    print(f"✅ Created setup instructions: {instructions_path}")
    
    print("\n📋 Next steps:")
    print("1. Follow the instructions in oracle-service/SWITCHBOARD_SETUP.md")
    print("2. Update your .env files with the oracle credentials")
    print("3. Test the oracle connection")
    print("\n🎉 Switchboard setup complete!")

if __name__ == "__main__":
    create_switchboard_config()
