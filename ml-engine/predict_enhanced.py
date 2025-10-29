import argparse
import hashlib
import json
import re
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import numpy as np

import torch
from transformers import AutoTokenizer

from model import CodeBERTMultiLabel


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract_line_numbers(code: str, vulnerability_type: str) -> List[int]:
    """Extract line numbers most likely associated with vulnerability patterns"""
    lines = code.split('\n')
    suspicious_lines = []
    
    # Vulnerability-specific pattern matching
    patterns = {
        'reentrancy': [
            r'\.call\s*\(',
            r'\.send\s*\(',
            r'\.transfer\s*\(',
            r'msg\.sender\.call\s*\(',
            r'\.delegatecall\s*\('
        ],
        'integer_overflow': [
            r'\+\s*[^=]',
            r'\*\s*[^=]',
            r'\.add\s*\(',
            r'\.mul\s*\(',
            r'\.sub\s*\('
        ],
        'access_control': [
            r'require\s*\(',
            r'onlyOwner',
            r'msg\.sender',
            r'\.only\w+',
            r'access control'
        ],
        'tx_origin': [
            r'tx\.origin',
            r'origin\s*=='
        ],
        'timestamp_dependency': [
            r'block\.timestamp',
            r'now\s*[<>=]',
            r'timestamp\s*[<>=]'
        ]
    }
    
    if vulnerability_type in patterns:
        for i, line in enumerate(lines):
            for pattern in patterns[vulnerability_type]:
                if re.search(pattern, line, re.IGNORECASE):
                    suspicious_lines.append(i + 1)
    
    return suspicious_lines[:5]  # Return top 5 suspicious lines


def generate_attention_heatmap(tokens: List[str], attention_weights: torch.Tensor, 
                             vulnerability_type: str, output_path: str = None) -> str:
    """Generate attention weight visualization"""
    if len(tokens) > 100:  # Limit for visualization
        tokens = tokens[:100]
        attention_weights = attention_weights[:100]
    
    plt.figure(figsize=(12, 6))
    attention_np = attention_weights.detach().cpu().numpy()
    
    # Create heatmap
    plt.imshow(attention_np.reshape(1, -1), cmap='Reds', aspect='auto')
    plt.colorbar()
    plt.title(f'Attention Weights for {vulnerability_type}')
    plt.xlabel('Token Position')
    plt.yticks([])
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        return output_path
    else:
        plt.show()
        return "heatmap_displayed"


def calculate_confidence_score(probability: float, line_evidence: List[int]) -> float:
    """Calculate confidence score based on probability and line evidence"""
    base_confidence = probability
    evidence_bonus = min(0.1, len(line_evidence) * 0.02)  # Small bonus for evidence
    return min(1.0, base_confidence + evidence_bonus)


def generate_ai_summary(predictions: List[Dict], risk_score: float) -> str:
    """Generate AI summary of vulnerability analysis"""
    high_risk_vulns = [p for p in predictions if p['probability'] > 0.7]
    medium_risk_vulns = [p for p in predictions if 0.4 <= p['probability'] <= 0.7]
    
    if risk_score > 0.8:
        severity = "HIGH RISK"
    elif risk_score > 0.5:
        severity = "MEDIUM RISK"
    else:
        severity = "LOW RISK"
    
    summary_parts = [f"Contract analysis shows {severity} with {len(high_risk_vulns)} critical vulnerabilities."]
    
    if high_risk_vulns:
        vuln_names = [v['vulnerability'] for v in high_risk_vulns]
        summary_parts.append(f"Critical issues: {', '.join(vuln_names[:3])}.")
    
    if len(high_risk_vulns) == 0 and medium_risk_vulns:
        summary_parts.append(f"Found {len(medium_risk_vulns)} moderate security concerns requiring review.")
    
    return " ".join(summary_parts)


def get_fix_suggestions(vulnerability_type: str) -> Dict[str, str]:
    """Get fix suggestions for vulnerability types"""
    suggestions = {
        'reentrancy': {
            'description': 'Use checks-effects-interactions pattern',
            'code_example': '// Use reentrancy guard\nmodifier nonReentrant() {\n    require(!locked, "Reentrant call");\n    locked = true;\n    _;\n    locked = false;\n}',
            'severity': 'CRITICAL'
        },
        'integer_overflow': {
            'description': 'Use SafeMath library or Solidity 0.8+ checked arithmetic',
            'code_example': '// Use SafeMath\nimport "@openzeppelin/contracts/utils/math/SafeMath.sol";\nusing SafeMath for uint256;',
            'severity': 'HIGH'
        },
        'access_control': {
            'description': 'Implement proper role-based access control',
            'code_example': 'modifier onlyOwner() {\n    require(msg.sender == owner, "Not owner");\n    _;\n}',
            'severity': 'HIGH'
        },
        'tx_origin': {
            'description': 'Use msg.sender instead of tx.origin for authentication',
            'code_example': '// Replace tx.origin with msg.sender\nrequire(msg.sender == owner, "Unauthorized");',
            'severity': 'MEDIUM'
        },
        'timestamp_dependency': {
            'description': 'Avoid using block.timestamp for critical logic',
            'code_example': '// Use commit-reveal scheme or oracle for time-sensitive operations',
            'severity': 'MEDIUM'
        }
    }
    
    return suggestions.get(vulnerability_type, {
        'description': 'Review contract logic and implement appropriate security measures',
        'code_example': '// Consult security best practices',
        'severity': 'UNKNOWN'
    })


@torch.no_grad()
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--source", type=str, required=True)
    parser.add_argument("--output-heatmap", action="store_true", help="Generate attention heatmap")
    args = parser.parse_args()

    ckpt = torch.load(args.model, map_location="cpu")
    cfg = ckpt["cfg"]
    label_space: Dict[str, int] = ckpt["label_space"]
    inv = {i: k for k, i in label_space.items()}

    with open(args.source, "r", encoding="utf-8") as f:
        code = f.read()

    tokenizer = AutoTokenizer.from_pretrained(cfg["model_name"])
    model = CodeBERTMultiLabel(cfg["model_name"], num_labels=len(label_space))
    model.load_state_dict(ckpt["state_dict"])
    model.eval()

    # Tokenize and get model outputs
    enc = tokenizer(code, max_length=cfg["max_length"], truncation=True, 
                   padding="max_length", return_tensors="pt")
    
    # Get attention weights if model supports it
    outputs = model.encoder(**enc, output_attentions=True)
    attention_weights = outputs.attentions[-1].mean(dim=1).squeeze()  # Last layer attention
    
    logits = model(enc["input_ids"], enc["attention_mask"]) 
    probs = torch.sigmoid(logits).squeeze(0).tolist()

    # Enhanced predictions with explainability
    enhanced_predictions = []
    all_fix_suggestions = {}
    
    for idx, p in enumerate(probs):
        vuln_type = inv[idx]
        if p > 0.3:  # Only include predictions above threshold
            line_evidence = extract_line_numbers(code, vuln_type)
            confidence = calculate_confidence_score(p, line_evidence)
            
            prediction = {
                "vulnerability": vuln_type,
                "probability": float(p),
                "confidence": float(confidence),
                "lines": line_evidence,
                "severity": "CRITICAL" if p > 0.8 else "HIGH" if p > 0.6 else "MEDIUM" if p > 0.4 else "LOW"
            }
            
            enhanced_predictions.append(prediction)
            all_fix_suggestions[vuln_type] = get_fix_suggestions(vuln_type)
            
            # Generate heatmap for high-confidence predictions
            if args.output_heatmap and p > 0.7:
                tokens = tokenizer.convert_ids_to_tokens(enc["input_ids"][0])
                heatmap_path = generate_attention_heatmap(
                    tokens, attention_weights, vuln_type, 
                    f"heatmap_{vuln_type}.png"
                )
                prediction["attention_heatmap"] = heatmap_path

    # Calculate enhanced risk score
    if enhanced_predictions:
        risk_score = sum([p["probability"] * (1.0 if p["severity"] == "CRITICAL" else 0.8 if p["severity"] == "HIGH" else 0.6) 
                         for p in enhanced_predictions]) / len(enhanced_predictions)
    else:
        risk_score = 0.0

    # Generate AI summary
    ai_summary = generate_ai_summary(enhanced_predictions, risk_score)

    # Final output
    out = {
        "contract_hash": sha256_hex(code),
        "predictions": enhanced_predictions,
        "risk_score": float(risk_score),
        "ai_summary": ai_summary,
        "fix_suggestions": all_fix_suggestions,
        "analysis_metadata": {
            "model_version": "1.0",
            "confidence_threshold": 0.3,
            "total_vulnerabilities_checked": len(label_space),
            "vulnerabilities_found": len(enhanced_predictions)
        }
    }
    
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
