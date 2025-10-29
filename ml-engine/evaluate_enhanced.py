import argparse
import torch
from torch.utils.data import DataLoader, Dataset
from transformers import AutoTokenizer
import yaml
import numpy as np
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score, classification_report
import json

from preprocessing import load_unified_json, build_label_space, multilabel_targets
from model import CodeBERTMultiLabel


class ContractsDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        enc = self.tokenizer(
            self.texts[idx],
            max_length=self.max_length,
            truncation=True,
            padding="max_length",
            return_tensors="pt",
        )
        item = {k: v.squeeze(0) for k, v in enc.items()}
        item["labels"] = torch.tensor(self.labels[idx], dtype=torch.float32)
        return item


@torch.no_grad()
def evaluate_model(model, dataloader, device, label_space):
    """Enhanced evaluation with detailed metrics"""
    model.eval()
    
    all_true = []
    all_pred = []
    all_probs = []
    
    for batch in dataloader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)
        
        logits = model(input_ids, attention_mask)
        probs = torch.sigmoid(logits).cpu().numpy()
        
        # Use different thresholds for prediction
        preds_05 = (probs > 0.5).astype(np.float32)
        preds_03 = (probs > 0.3).astype(np.float32)
        
        all_probs.append(probs)
        all_true.append(labels.cpu().numpy())
        
        # Use 0.3 threshold for more sensitive detection
        all_pred.append(preds_03)
    
    y_true = np.vstack(all_true)
    y_pred = np.vstack(all_pred)
    y_probs = np.vstack(all_probs)
    
    # Calculate metrics
    micro_f1 = f1_score(y_true, y_pred, average="micro", zero_division=0)
    macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
    micro_precision = precision_score(y_true, y_pred, average="micro", zero_division=0)
    micro_recall = recall_score(y_true, y_pred, average="micro", zero_division=0)
    
    # Per-class metrics
    f1_per_class = f1_score(y_true, y_pred, average=None, zero_division=0)
    
    # Calculate accuracy for multilabel
    accuracy = accuracy_score(y_true, y_pred)
    
    # Count positive examples
    positive_examples = np.sum(y_true, axis=0)
    predicted_examples = np.sum(y_pred, axis=0)
    
    print(f"Dataset Statistics:")
    print(f"  Total samples: {len(y_true)}")
    print(f"  Positive examples per class:")
    inv_label_space = {v: k for k, v in label_space.items()}
    for i, count in enumerate(positive_examples):
        if count > 0:
            print(f"    {inv_label_space[i]}: {int(count)}")
    
    print(f"\nModel Performance:")
    print(f"  Micro F1: {micro_f1:.4f}")
    print(f"  Macro F1: {macro_f1:.4f}")
    print(f"  Micro Precision: {micro_precision:.4f}")
    print(f"  Micro Recall: {micro_recall:.4f}")
    print(f"  Accuracy: {accuracy:.4f}")
    
    print(f"\nPer-Class F1 Scores:")
    for i, f1 in enumerate(f1_per_class):
        if positive_examples[i] > 0:  # Only show classes with positive examples
            print(f"  {inv_label_space[i]}: {f1:.4f} (pos: {int(positive_examples[i])}, pred: {int(predicted_examples[i])})")
    
    # Show some prediction examples
    print(f"\nSample Predictions:")
    for i in range(min(5, len(y_true))):
        true_labels = [inv_label_space[j] for j in range(len(y_true[i])) if y_true[i][j] > 0]
        pred_labels = [inv_label_space[j] for j in range(len(y_pred[i])) if y_pred[i][j] > 0]
        print(f"  Sample {i}: True={true_labels}, Pred={pred_labels}")
    
    return {
        "micro_f1": micro_f1,
        "macro_f1": macro_f1,
        "micro_precision": micro_precision,
        "micro_recall": micro_recall,
        "accuracy": accuracy,
        "f1_per_class": dict(zip([inv_label_space[i] for i in range(len(f1_per_class))], f1_per_class.tolist()))
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, required=True)
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--threshold", type=float, default=0.3)
    args = parser.parse_args()

    print(f"Loading model from {args.model}")
    ckpt = torch.load(args.model, map_location="cpu")
    cfg = ckpt["cfg"]
    label_space = ckpt["label_space"]
    
    print(f"Loading dataset from {args.data}")
    df = load_unified_json(args.data)
    print(f"Dataset loaded: {len(df)} samples")
    
    # Check data distribution
    vuln_count = sum(1 for vulns in df["vulnerabilities"] if vulns)
    print(f"Vulnerable contracts: {vuln_count}/{len(df)}")
    
    tokenizer = AutoTokenizer.from_pretrained(cfg["model_name"])
    labels = multilabel_targets(df["vulnerabilities"].tolist(), label_space)
    
    dataset = ContractsDataset(
        df["source_code"].tolist(), labels, tokenizer, cfg["max_length"]
    )

    loader = DataLoader(dataset, batch_size=args.batch_size)
    model = CodeBERTMultiLabel(cfg["model_name"], num_labels=len(label_space))
    model.load_state_dict(ckpt["state_dict"])
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    
    print(f"Using device: {device}")
    
    # Evaluate model
    metrics = evaluate_model(model, loader, device, label_space)
    
    # Save results
    with open("evaluation_results.json", "w") as f:
        json.dump(metrics, f, indent=2)
    
    print(f"\nResults saved to evaluation_results.json")


if __name__ == "__main__":
    main()
