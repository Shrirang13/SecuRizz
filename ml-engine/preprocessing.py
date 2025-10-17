import json
import os
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


def load_unified_json(dataset_path: str) -> pd.DataFrame:
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return pd.DataFrame(data)


def build_label_space(vulnerability_types: List[str]) -> Dict[str, int]:
    return {v: i for i, v in enumerate(vulnerability_types)}


def multilabel_targets(labels: List[List[str]], label_space: Dict[str, int]) -> np.ndarray:
    y = np.zeros((len(labels), len(label_space)), dtype=np.float32)
    for row_idx, lab_list in enumerate(labels):
        for lab in lab_list:
            if lab in label_space:
                y[row_idx, label_space[lab]] = 1.0
    return y


def train_val_split(df: pd.DataFrame, val_ratio: float = 0.1, seed: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    split = int(len(df) * (1 - val_ratio))
    return df.iloc[:split], df.iloc[split:]


