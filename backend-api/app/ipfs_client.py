#!/usr/bin/env python3
"""
Enhanced Pinata IPFS client with real Web3 integration
"""

import requests
import json
import os
from typing import Dict, Any, Optional
import hashlib
from datetime import datetime

class PinataIPFSClient:
    def __init__(self):
        self.api_key = os.getenv("PINATA_API_KEY")
        self.secret_key = os.getenv("PINATA_SECRET_KEY")
        self.base_url = "https://api.pinata.cloud"
        self.gateway_url = "https://gateway.pinata.cloud/ipfs"
        
        if not self.api_key or not self.secret_key:
            print("WARNING: PINATA_API_KEY and PINATA_SECRET_KEY not set - using mock IPFS")
            self.mock_mode = True
        else:
            self.mock_mode = False

    def pin_json(self, data: Dict[str, Any], name: str) -> str:
        """Pin JSON data to IPFS and return CID"""
        if hasattr(self, 'mock_mode') and self.mock_mode:
            # Mock mode - return a hash
            content = json.dumps(data, sort_keys=True)
            cid = hashlib.sha256(content.encode()).hexdigest()
            print(f"Mock IPFS: {cid}")
            return cid
            
        try:
            # Add metadata
            metadata = {
                "name": name,
                "description": f"SecuRizz audit report - {name}",
                "keyvalues": {
                    "app": "SecuRizz",
                    "type": "audit_report",
                    "timestamp": datetime.utcnow().isoformat(),
                    "version": "1.0"
                }
            }
            
            # Prepare pin data
            pin_data = {
                "pinataContent": data,
                "pinataMetadata": metadata,
                "pinataOptions": {
                    "cidVersion": 1,
                    "wrapWithDirectory": False
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "pinata_api_key": self.api_key,
                "pinata_secret_api_key": self.secret_key
            }
            
            response = requests.post(
                f"{self.base_url}/pinning/pinJSONToIPFS",
                headers=headers,
                json=pin_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                cid = result["IpfsHash"]
                print(f"✅ Pinned to IPFS: {cid}")
                return cid
            else:
                raise Exception(f"Pinata API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ IPFS pinning failed: {str(e)}")
            # Fallback to local hash
            content = json.dumps(data, sort_keys=True)
            return hashlib.sha256(content.encode()).hexdigest()

    def get_from_ipfs(self, cid: str) -> Optional[Dict[str, Any]]:
        """Retrieve data from IPFS"""
        try:
            response = requests.get(f"{self.gateway_url}/{cid}", timeout=30)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"❌ Failed to retrieve from IPFS: {str(e)}")
            return None

    def verify_pin(self, cid: str) -> bool:
        """Verify that content is pinned and accessible"""
        try:
            data = self.get_from_ipfs(cid)
            return data is not None
        except:
            return False

    def get_pin_list(self) -> list:
        """Get list of all pinned content"""
        try:
            headers = {
                "pinata_api_key": self.api_key,
                "pinata_secret_api_key": self.secret_key
            }
            
            response = requests.get(
                f"{self.base_url}/data/pinList",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get("rows", [])
            return []
        except Exception as e:
            print(f"❌ Failed to get pin list: {str(e)}")
            return []

# Global instance
ipfs_client = PinataIPFSClient()