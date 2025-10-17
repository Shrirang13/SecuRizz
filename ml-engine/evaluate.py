import argparse
import torch
from torch.utils.data import DataLoader, Dataset
from transformers import AutoTokenizer
import yaml
import numpy as np
from sklearn.metrics import f1_score

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
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, required=True)
    parser.add_argument("--model", type=str, required=True)
    args = parser.parse_args()

    ckpt = torch.load(args.model, map_location="cpu")
    cfg = ckpt["cfg"]
    label_space = ckpt["label_space"]
    inv = {i: k for k, i in label_space.items()}

    df = load_unified_json(args.data)
    tokenizer = AutoTokenizer.from_pretrained(cfg["model_name"])
    labels = multilabel_targets(df["vulnerabilities"].tolist(), label_space)
    dataset = ContractsDataset(
        df["source_code"].tolist(), labels, tokenizer, cfg["max_length"]
    )

    loader = DataLoader(dataset, batch_size=4)
    model = CodeBERTMultiLabel(cfg["model_name"], num_labels=len(label_space))
    model.load_state_dict(ckpt["state_dict"])
    model.eval()

    all_true, all_pred = [], []
    for batch in loader:
        logits = model(batch["input_ids"], batch["attention_mask"])
        probs = torch.sigmoid(logits).cpu().numpy()
        preds = (probs > 0.5).astype(np.float32)
        all_pred.append(preds)
        all_true.append(batch["labels"].numpy())

    y_true = np.vstack(all_true)
    y_pred = np.vstack(all_pred)
    micro_f1 = f1_score(y_true, y_pred, average="micro")
    macro_f1 = f1_score(y_true, y_pred, average="macro")
    print({"micro_f1": micro_f1, "macro_f1": macro_f1})


if __name__ == "__main__":
    main()


