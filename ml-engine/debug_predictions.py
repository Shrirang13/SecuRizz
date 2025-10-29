import torch
import numpy as np
from transformers import AutoTokenizer
from model import CodeBERTMultiLabel
import json

def debug_model_predictions():
    """Debug model predictions to understand why it's not detecting vulnerabilities"""
    
    # Load model
    ckpt = torch.load('models/codebert_multilabel.pt', map_location='cpu')
    cfg = ckpt["cfg"]
    label_space = ckpt["label_space"]
    
    tokenizer = AutoTokenizer.from_pretrained(cfg["model_name"])
    model = CodeBERTMultiLabel(cfg["model_name"], num_labels=len(label_space))
    model.load_state_dict(ckpt["state_dict"])
    model.eval()
    
    # Load a sample of vulnerable code
    with open('../datasets/processed/unified_dataset.json', 'r') as f:
        data = json.load(f)
    
    # Find a vulnerable contract
    vulnerable_sample = None
    for item in data:
        if item['vulnerabilities']:
            vulnerable_sample = item
            break
    
    if not vulnerable_sample:
        print("No vulnerable samples found!")
        return
    
    print(f"Testing vulnerable sample: {vulnerable_sample['contract_id']}")
    print(f"Expected vulnerabilities: {vulnerable_sample['vulnerabilities']}")
    print(f"Code preview: {vulnerable_sample['source_code'][:200]}...")
    
    # Tokenize and predict
    enc = tokenizer(
        vulnerable_sample['source_code'],
        max_length=cfg["max_length"],
        truncation=True,
        padding="max_length",
        return_tensors="pt"
    )
    
    with torch.no_grad():
        logits = model(enc["input_ids"], enc["attention_mask"])
        probs = torch.sigmoid(logits).squeeze(0).numpy()
    
    print(f"\nRaw probabilities:")
    inv_label_space = {v: k for k, v in label_space.items()}
    for i, prob in enumerate(probs):
        print(f"  {inv_label_space[i]}: {prob:.4f}")
    
    # Check different thresholds
    thresholds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    print(f"\nPredictions at different thresholds:")
    for threshold in thresholds:
        preds = [inv_label_space[i] for i, prob in enumerate(probs) if prob > threshold]
        print(f"  Threshold {threshold}: {preds}")
    
    # Check if model outputs are reasonable
    print(f"\nModel statistics:")
    print(f"  Max probability: {np.max(probs):.4f}")
    print(f"  Min probability: {np.min(probs):.4f}")
    print(f"  Mean probability: {np.mean(probs):.4f}")
    print(f"  Std probability: {np.std(probs):.4f}")
    
    # Test with a safe contract too
    safe_sample = None
    for item in data:
        if not item['vulnerabilities']:
            safe_sample = item
            break
    
    if safe_sample:
        print(f"\nTesting safe sample: {safe_sample['contract_id']}")
        enc_safe = tokenizer(
            safe_sample['source_code'],
            max_length=cfg["max_length"],
            truncation=True,
            padding="max_length",
            return_tensors="pt"
        )
        
        with torch.no_grad():
            logits_safe = model(enc_safe["input_ids"], enc_safe["attention_mask"])
            probs_safe = torch.sigmoid(logits_safe).squeeze(0).numpy()
        
        print(f"Safe sample max probability: {np.max(probs_safe):.4f}")
        print(f"Safe sample mean probability: {np.mean(probs_safe):.4f}")

if __name__ == "__main__":
    debug_model_predictions()
