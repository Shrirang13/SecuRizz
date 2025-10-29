import subprocess
import json
import tempfile
import os
import sys
from typing import List, Dict
import hashlib

# Add the ml-engine directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'ml-engine'))
from language_detector import language_detector


class MLClient:
    def __init__(self, model_path: str = "ml-engine/models/codebert_multilabel.pt"):
        self.model_path = model_path
        
    def analyze_contract(self, source_code: str) -> Dict:
        # First, validate the input
        validation_result = language_detector.validate_input(source_code)
        
        if not validation_result['is_valid']:
            return {
                "contract_hash": hashlib.sha256(source_code.encode()).hexdigest(),
                "predictions": [],
                "risk_score": 0.0,
                "validation_errors": validation_result['errors'],
                "language": validation_result['language'],
                "is_code": validation_result['is_code']
            }
        
        # Determine file extension based on detected language
        file_extensions = {
            'solidity': '.sol',
            'vyper': '.vy',
            'rust': '.rs',
            'javascript': '.js',
            'python': '.py'
        }
        
        file_ext = file_extensions.get(validation_result['language'], '.sol')
        
        with tempfile.NamedTemporaryFile(mode='w', suffix=file_ext, delete=False) as f:
            f.write(source_code)
            temp_path = f.name
        
        try:
            cmd = [
                "python", "ml-engine/predict_enhanced.py",
                "--model", self.model_path,
                "--source", temp_path,
                "--output-heatmap"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.dirname(__file__))
            )
            
            if result.returncode != 0:
                print(f"ML analysis failed: {result.stderr}")
                return self._fallback_analysis(source_code, validation_result)
            
            ml_result = json.loads(result.stdout)
            ml_result['language'] = validation_result['language']
            ml_result['is_code'] = validation_result['is_code']
            return ml_result
            
        except Exception as e:
            print(f"ML analysis error: {e}")
            return self._fallback_analysis(source_code, validation_result)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def _fallback_analysis(self, source_code: str, validation_result: Dict = None) -> Dict:
        vulnerabilities = []
        risk_score = 0.0
        
        # Enhanced pattern-based detection
        patterns = {
            "reentrancy": [
                r"\.call\s*\{[^}]*value[^}]*\}",
                r"\.transfer\s*\(",
                r"\.send\s*\(",
                r"external\s+payable",
                r"msg\.value"
            ],
            "tx_origin": [
                r"tx\.origin",
                r"msg\.sender.*tx\.origin"
            ],
            "unsafe_selfdestruct": [
                r"selfdestruct\s*\(",
                r"suicide\s*\("
            ],
            "delegatecall": [
                r"delegatecall\s*\(",
                r"\.delegatecall\s*\("
            ],
            "timestamp_dependency": [
                r"block\.timestamp",
                r"now\s*[<>=]",
                r"block\.number"
            ],
            "integer_overflow": [
                r"\+\+",
                r"--",
                r"\+\s*=",
                r"-\s*=",
                r"\*\s*=",
                r"/\s*="
            ],
            "access_control": [
                r"public\s+function",
                r"external\s+function",
                r"onlyOwner",
                r"modifier\s+\w+"
            ],
            "unchecked_calls": [
                r"\.call\s*\(",
                r"\.delegatecall\s*\(",
                r"\.staticcall\s*\("
            ]
        }
        
        import re
        
        for vuln_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, source_code, re.IGNORECASE):
                    # Calculate probability based on pattern complexity and context
                    probability = 0.6
                    
                    # Boost probability for critical patterns
                    if vuln_type in ["reentrancy", "tx_origin", "unsafe_selfdestruct"]:
                        probability = 0.8
                    elif vuln_type in ["delegatecall", "unchecked_calls"]:
                        probability = 0.7
                    
                    vulnerabilities.append({
                        "vulnerability": vuln_type,
                        "probability": probability
                    })
                    risk_score += probability
                    break  # Only add once per vulnerability type
        
        # Normalize risk score
        if vulnerabilities:
            risk_score = min(risk_score / len(vulnerabilities), 1.0)
        
        result = {
            "contract_hash": hashlib.sha256(source_code.encode()).hexdigest(),
            "predictions": vulnerabilities,
            "risk_score": risk_score
        }
        
        # Add validation info if available
        if validation_result:
            result['language'] = validation_result['language']
            result['is_code'] = validation_result['is_code']
            if 'validation_errors' in validation_result:
                result['validation_errors'] = validation_result['errors']
        
        return result


ml_client = MLClient()
