import requests
import os
from typing import Optional


class PinataClient:
    def __init__(self):
        self.jwt = os.getenv("PINATA_JWT")
        self.base_url = "https://api.pinata.cloud"
        
    def pin_json(self, data: dict, name: str) -> Optional[str]:
        if not self.jwt:
            print("Warning: PINATA_JWT not set, skipping IPFS upload")
            return None
            
        headers = {
            "Authorization": f"Bearer {self.jwt}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "pinataContent": data,
            "pinataMetadata": {
                "name": name
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/pinning/pinJSONToIPFS",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result.get("IpfsHash")
        except Exception as e:
            print(f"Failed to pin to IPFS: {e}")
            return None
    
    def get_json(self, cid: str) -> Optional[dict]:
        try:
            response = requests.get(
                f"https://gateway.pinata.cloud/ipfs/{cid}",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Failed to retrieve from IPFS: {e}")
            return None


ipfs_client = PinataClient()
