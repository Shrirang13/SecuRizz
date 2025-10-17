import argparse
import json
from pathlib import Path

import torch
from torch.utils.data import DataLoader, Dataset
from transformers import AutoTokenizer
import yaml

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


def train_epoch(model, dataloader, optimizer, device):
    model.train()
    total = 0.0
    for batch in dataloader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)
        logits = model(input_ids, attention_mask)
        loss = model.loss_fn(logits, labels)
        loss.backward()
        optimizer.step()
        optimizer.zero_grad(set_to_none=True)
        total += loss.item()
    return total / max(1, len(dataloader))


@torch.no_grad()
def eval_epoch(model, dataloader, device):
    model.eval()
    total = 0.0
    for batch in dataloader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)
        logits = model(input_ids, attention_mask)
        loss = model.loss_fn(logits, labels)
        total += loss.item()
    return total / max(1, len(dataloader))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, required=True, help="Path to unified JSON dataset")
    parser.add_argument("--config", type=str, default="config.yaml")
    parser.add_argument("--out", type=str, default="models/codebert_multilabel.pt")
    parser.add_argument("--batch", type=int, default=4)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--lr", type=float, default=5e-5)
    args = parser.parse_args()

    cfg = yaml.safe_load(open(args.config))
    vulns = cfg["vulnerability_types"]
    label_space = build_label_space(vulns)

    df = load_unified_json(args.data)
    texts = df["source_code"].tolist()
    labels = multilabel_targets(df["vulnerabilities"].tolist(), label_space)

    train_df, val_df = train_val_split(df)
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
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)

    train_loader = DataLoader(train_dataset, batch_size=args.batch, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch)

    for epoch in range(args.epochs):
        tr_loss = train_epoch(model, train_loader, optimizer, device)
        va_loss = eval_epoch(model, val_loader, device)
        print(f"epoch={epoch} train_loss={tr_loss:.4f} val_loss={va_loss:.4f}")

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    torch.save({"state_dict": model.state_dict(), "label_space": label_space, "cfg": cfg}, args.out)
    print(f"saved model to {args.out}")


if __name__ == "__main__":
    main()


