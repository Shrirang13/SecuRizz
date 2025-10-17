import subprocess
import json
import tempfile
import os
from typing import List, Dict
import hashlib


class MLClient:
    def __init__(self, model_path: str = "ml-engine/models/codebert_multilabel.pt"):
        self.model_path = model_path
        
    def analyze_contract(self, source_code: str) -> Dict:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sol', delete=False) as f:
            f.write(source_code)
            temp_path = f.name
        
        try:
            cmd = [
                "python", "ml-engine/predict.py",
                "--model", self.model_path,
                "--source", temp_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.dirname(__file__))
            )
            
            if result.returncode != 0:
                print(f"ML analysis failed: {result.stderr}")
                return self._fallback_analysis(source_code)
            
            return json.loads(result.stdout)
            
        except Exception as e:
            print(f"ML analysis error: {e}")
            return self._fallback_analysis(source_code)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def _fallback_analysis(self, source_code: str) -> Dict:
        vulnerabilities = []
        risk_score = 0.0
        
        if "msg.sender" in source_code and "tx.origin" in source_code:
            vulnerabilities.append({"vulnerability": "tx_origin", "probability": 0.8})
            risk_score += 0.8
            
        if "selfdestruct" in source_code:
            vulnerabilities.append({"vulnerability": "unsafe_selfdestruct", "probability": 0.7})
            risk_score += 0.7
            
        if "delegatecall" in source_code:
            vulnerabilities.append({"vulnerability": "delegatecall", "probability": 0.6})
            risk_score += 0.6
            
        if "block.timestamp" in source_code:
            vulnerabilities.append({"vulnerability": "timestamp_dependency", "probability": 0.5})
            risk_score += 0.5
            
        risk_score = min(risk_score / max(1, len(vulnerabilities)), 1.0)
        
        return {
            "contract_hash": hashlib.sha256(source_code.encode()).hexdigest(),
            "predictions": vulnerabilities,
            "risk_score": risk_score
        }


ml_client = MLClient()
