#!/usr/bin/env python3
"""
SecuRizz Program ID Update Script

This script updates the Solana program ID across all configuration files
after deployment to devnet.

Usage:
    python scripts/update_program_id.py <PROGRAM_ID>
    
Example:
    python scripts/update_program_id.py 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM
"""

import sys
import os
import re
from pathlib import Path

def update_file(file_path, old_pattern, new_value):
    """Update a file with new program ID"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Replace the pattern
        new_content = re.sub(old_pattern, new_value, content)
        
        if content != new_content:
            with open(file_path, 'w') as f:
                f.write(new_content)
            print(f"✅ Updated {file_path}")
            return True
        else:
            print(f"⚠️  No changes needed in {file_path}")
            return False
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/update_program_id.py <PROGRAM_ID>")
        print("Example: python scripts/update_program_id.py 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM")
        sys.exit(1)
    
    program_id = sys.argv[1]
    
    # Validate program ID format (base58, 32-44 characters)
    if not re.match(r'^[1-9A-HJ-NP-Za-km-z]{32,44}$', program_id):
        print("❌ Invalid program ID format. Must be a valid Solana public key.")
        sys.exit(1)
    
    print(f"🔄 Updating program ID to: {program_id}")
    print("=" * 50)
    
    # Files to update
    files_to_update = [
        {
            'path': 'solana-contract/Anchor.toml',
            'pattern': r'securizz = "ReplaceWithDeployedProgramId"',
            'replacement': f'securizz = "{program_id}"'
        },
        {
            'path': 'solana-contract/programs/securizz/src/lib.rs',
            'pattern': r'declare_id!\("ReplaceWithDeployedProgramId"\);',
            'replacement': f'declare_id!("{program_id}");'
        },
        {
            'path': 'backend-api/env.example',
            'pattern': r'SOLANA_PROGRAM_ID=ReplaceWithDeployedProgramId',
            'replacement': f'SOLANA_PROGRAM_ID={program_id}'
        },
        {
            'path': 'oracle-service/env.example',
            'pattern': r'SOLANA_PROGRAM_ID=ReplaceWithDeployedProgramId',
            'replacement': f'SOLANA_PROGRAM_ID={program_id}'
        },
        {
            'path': 'frontend/env.example',
            'pattern': r'NEXT_PUBLIC_PROGRAM_ID=ReplaceWithDeployedProgramId',
            'replacement': f'NEXT_PUBLIC_PROGRAM_ID={program_id}'
        },
        {
            'path': 'env.example',
            'pattern': r'SOLANA_PROGRAM_ID=ReplaceWithDeployedProgramId',
            'replacement': f'SOLANA_PROGRAM_ID={program_id}'
        }
    ]
    
    updated_count = 0
    total_files = len(files_to_update)
    
    for file_info in files_to_update:
        file_path = Path(file_info['path'])
        if file_path.exists():
            if update_file(file_path, file_info['pattern'], file_info['replacement']):
                updated_count += 1
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print("=" * 50)
    print(f"✅ Updated {updated_count}/{total_files} files")
    
    if updated_count > 0:
        print("\n📋 Next steps:")
        print("1. Copy the updated .env.example files to .env in each service")
        print("2. Fill in your API keys (Pinata, Switchboard, etc.)")
        print("3. Restart all services")
        print("\n🎉 Program ID update complete!")
    else:
        print("❌ No files were updated. Please check the program ID format.")

if __name__ == "__main__":
    main()
