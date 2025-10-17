import argparse
import hashlib
import json
from typing import Dict, List

import torch
from transformers import AutoTokenizer

from model import CodeBERTMultiLabel


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@torch.no_grad()
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--source", type=str, required=True)
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

    enc = tokenizer(code, max_length=cfg["max_length"], truncation=True, padding="max_length", return_tensors="pt")
    logits = model(enc["input_ids"], enc["attention_mask"]) 
    probs = torch.sigmoid(logits).squeeze(0).tolist()

    results = []
    for idx, p in enumerate(probs):
        results.append({"vulnerability": inv[idx], "probability": float(p)})

    out = {
        "contract_hash": sha256_hex(code),
        "predictions": results,
        "risk_score": sum([r["probability"] for r in results]) / max(1, len(results))
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()


