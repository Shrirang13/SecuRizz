from typing import List

import torch
from torch import nn
from transformers import AutoConfig, AutoModel


class CodeBERTMultiLabel(nn.Module):
    def __init__(self, model_name: str, num_labels: int):
        super().__init__()
        self.config = AutoConfig.from_pretrained(model_name)
        self.encoder = AutoModel.from_pretrained(model_name, config=self.config)
        hidden_size = getattr(self.config, "hidden_size", 768)
        self.classifier = nn.Sequential(
            nn.Dropout(0.1),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size, num_labels),
        )

    def forward(self, input_ids, attention_mask):
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        pooled = outputs.last_hidden_state[:, 0]
        logits = self.classifier(pooled)
        return logits

    @staticmethod
    def loss_fn(logits: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        return nn.BCEWithLogitsLoss()(logits, labels)

    @staticmethod
    def predict_proba(logits: torch.Tensor) -> torch.Tensor:
        return torch.sigmoid(logits)


