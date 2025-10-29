import argparse
import json
from pathlib import Path
import time

import torch
from torch.utils.data import DataLoader, Dataset
from transformers import AutoTokenizer, get_linear_schedule_with_warmup
import yaml
import numpy as np
from sklearn.metrics import f1_score

from preprocessing import load_unified_json, build_label_space, multilabel_targets, train_val_split
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


def train_epoch(model, dataloader, optimizer, scheduler, device):
    model.train()
    total_loss = 0.0
    all_preds = []
    all_labels = []
    
    for batch_idx, batch in enumerate(dataloader):
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)
        
        optimizer.zero_grad()
        logits = model(input_ids, attention_mask)
        loss = model.loss_fn(logits, labels)
        loss.backward()
        
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        
        optimizer.step()
        scheduler.step()
        
        total_loss += loss.item()
        
        # Collect predictions for F1 calculation
        with torch.no_grad():
            probs = torch.sigmoid(logits)
            preds = (probs > 0.3).float()
            all_preds.append(preds.cpu().numpy())
            all_labels.append(labels.cpu().numpy())
    
    # Calculate F1 score
    if all_preds:
        y_pred = np.vstack(all_preds)
        y_true = np.vstack(all_labels)
        f1 = f1_score(y_true, y_pred, average="micro", zero_division=0)
        return total_loss / len(dataloader), f1
    else:
        return total_loss / len(dataloader), 0.0


@torch.no_grad()
def eval_epoch(model, dataloader, device):
    model.eval()
    total_loss = 0.0
    all_preds = []
    all_labels = []
    
    for batch in dataloader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)
        
        logits = model(input_ids, attention_mask)
        loss = model.loss_fn(logits, labels)
        total_loss += loss.item()
        
        # Collect predictions for F1 calculation
        probs = torch.sigmoid(logits)
        preds = (probs > 0.3).float()
        all_preds.append(preds.cpu().numpy())
        all_labels.append(labels.cpu().numpy())
    
    # Calculate F1 score
    if all_preds:
        y_pred = np.vstack(all_preds)
        y_true = np.vstack(all_labels)
        f1 = f1_score(y_true, y_pred, average="micro", zero_division=0)
        return total_loss / len(dataloader), f1
    else:
        return total_loss / len(dataloader), 0.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, required=True, help="Path to unified JSON dataset")
    parser.add_argument("--config", type=str, default="config.yaml")
    parser.add_argument("--out", type=str, default="models/codebert_enhanced.pt")
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--warmup-steps", type=int, default=100)
    parser.add_argument("--val-ratio", type=float, default=0.2)
    args = parser.parse_args()

    print(f"Starting enhanced training...")
    print(f"Dataset: {args.data}")
    print(f"Output: {args.out}")
    print(f"Epochs: {args.epochs}, Batch size: {args.batch}, LR: {args.lr}")

    cfg = yaml.safe_load(open(args.config))
    vulns = cfg["vulnerability_types"]
    label_space = build_label_space(vulns)

    print(f"Loading dataset...")
    df = load_unified_json(args.data)
    print(f"Dataset loaded: {len(df)} samples")
    
    # Check data distribution
    vuln_count = sum(1 for vulns in df["vulnerabilities"] if vulns)
    print(f"Vulnerable contracts: {vuln_count}/{len(df)}")

    texts = df["source_code"].tolist()
    labels = multilabel_targets(df["vulnerabilities"].tolist(), label_space)

    train_df, val_df = train_val_split(df, val_ratio=args.val_ratio)
    print(f"Train/Val split: {len(train_df)}/{len(val_df)}")

    tokenizer = AutoTokenizer.from_pretrained(cfg["model_name"])

    train_dataset = ContractsDataset(
        train_df["source_code"].tolist(),
        multilabel_targets(train_df["vulnerabilities"].tolist(), label_space),
        tokenizer,
        cfg["max_length"],
    )
    val_dataset = ContractsDataset(
        val_df["source_code"].tolist(),
        multilabel_targets(val_df["vulnerabilities"].tolist(), label_space),
        tokenizer,
        cfg["max_length"],
    )

    model = CodeBERTMultiLabel(cfg["model_name"], num_labels=len(label_space))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    print(f"Using device: {device}")

    # Enhanced optimizer with weight decay
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    
    train_loader = DataLoader(train_dataset, batch_size=args.batch, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch)

    # Learning rate scheduler
    total_steps = len(train_loader) * args.epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=args.warmup_steps,
        num_training_steps=total_steps
    )

    # Training loop with early stopping
    best_f1 = 0.0
    patience = 3
    patience_counter = 0
    
    training_history = {
        "train_loss": [],
        "train_f1": [],
        "val_loss": [],
        "val_f1": []
    }

    print(f"\nStarting training...")
    for epoch in range(args.epochs):
        start_time = time.time()
        
        tr_loss, tr_f1 = train_epoch(model, train_loader, optimizer, scheduler, device)
        va_loss, va_f1 = eval_epoch(model, val_loader, device)
        
        epoch_time = time.time() - start_time
        
        print(f"Epoch {epoch+1}/{args.epochs} ({epoch_time:.1f}s)")
        print(f"  Train Loss: {tr_loss:.4f}, Train F1: {tr_f1:.4f}")
        print(f"  Val Loss: {va_loss:.4f}, Val F1: {va_f1:.4f}")
        
        training_history["train_loss"].append(tr_loss)
        training_history["train_f1"].append(tr_f1)
        training_history["val_loss"].append(va_loss)
        training_history["val_f1"].append(va_f1)
        
        # Early stopping
        if va_f1 > best_f1:
            best_f1 = va_f1
            patience_counter = 0
            # Save best model
            Path(args.out).parent.mkdir(parents=True, exist_ok=True)
            torch.save({
                "state_dict": model.state_dict(),
                "label_space": label_space,
                "cfg": cfg,
                "training_history": training_history,
                "best_f1": best_f1
            }, args.out)
            print(f"  New best F1: {best_f1:.4f} - Model saved!")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"  Early stopping after {epoch+1} epochs")
                break

    print(f"\nTraining completed!")
    print(f"Best validation F1: {best_f1:.4f}")
    print(f"Model saved to: {args.out}")
    
    # Save training history
    with open(f"{args.out}.history.json", "w") as f:
        json.dump(training_history, f, indent=2)


if __name__ == "__main__":
    main()
