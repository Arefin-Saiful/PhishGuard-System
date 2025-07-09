import os
from urllib.parse import urlparse
from pathlib import Path
import json, logging
from typing import List, Union

import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import tokenizer_from_json
import joblib

# ────────────────────────────────────────────────────────────────
# Configuration: whitelist of known-safe domains
WHITELIST = {
    "github.com",
    "youtube.com",
    "wikipedia.org",
    "reddit.com",
    # Add other trusted domains here
}

# ─────────────────────────── paths ─────────────────────────────
BASE_DIR  = Path(__file__).resolve().parents[1]
MODEL_DIR = BASE_DIR / "models" / "URL"

def _need(name: str) -> Path:
    p = MODEL_DIR / name
    if not p.exists() or p.stat().st_size == 0:
        raise FileNotFoundError(f"[url_model] missing artefact → {p}")
    return p

# ───────────────────────── artefact loading ─────────────────────
with open(_need("tokenizer.json"), encoding="utf-8") as fh:
    TOKENIZER = tokenizer_from_json(fh.read())
_cfg = json.loads(_need("config.json").read_text())
MAX_LEN = int(_cfg["max_seq_len"])
LABEL_MAPPING: dict[str, int] = _cfg["label_mapping"]
IDX_TO_LABEL = {v: k for k, v in LABEL_MAPPING.items()}

MODEL = tf.keras.models.load_model(_need("Hybrid_CNN_LSTM_best.h5"), compile=False)
N_INPUTS = len(MODEL.inputs)  # 1 or 2

# ─────────────────── feature-scaling setup ─────────────────────
SCALER = joblib.load(_need("scaler_link_count.pkl"))

# ───────────────────────── feature builder ──────────────────────
def build_extra_features(urls: List[str]) -> np.ndarray:
    """
    Build numeric feature array of shape (n,7) then scale.
    Features per URL:
      1) length, 2) dot count, 3) slash count,
      4) hyphen count, 5) digit count, 6) '?' count, 7) '&' count
    """
    feats = []
    for raw in urls:
        u = raw.lower().strip()
        if not u.startswith(("http://", "https://")):
            u = "http://" + u
        path = urlparse(u).netloc.removeprefix("www.") + urlparse(u).path
        feats.append([
            float(len(path)),
            float(path.count('.')),
            float(path.count('/')),
            float(path.count('-')),
            float(sum(ch.isdigit() for ch in path)),
            float(path.count('?')),
            float(path.count('&'))
        ])
    arr = np.asarray(feats, dtype="float32")
    return SCALER.transform(arr)

# ───────────────────────── preprocessing ────────────────────────
def _tokenise(text: str) -> np.ndarray:
    seq = TOKENIZER.texts_to_sequences([text])[0]
    seq = (seq + [0] * MAX_LEN)[:MAX_LEN]
    return np.array([seq], dtype="int32")


def _preprocess(raw_url: str) -> Union[np.ndarray, List[np.ndarray]]:
    """
    Returns inputs for the model:
      - single numpy (1,MAX_LEN) if N_INPUTS==1
      - [seq, extra] if N_INPUTS==2
    """
    # normalize URL
    u = raw_url.strip()
    if not u.lower().startswith(("http://", "https://")):
        u = "http://" + u
    # strip www, keep path
    clean = urlparse(u).netloc.removeprefix("www.") + urlparse(u).path

    seq = _tokenise(clean)
    if N_INPUTS == 1:
        return seq

    extra = build_extra_features([raw_url])  # use original raw for features
    return [seq, extra]

# ───────────────────────── public API ─────────────────────────
def predict(raw_url: str) -> tuple[str, float]:
    """
    Returns ("Legitimate"|"Phishing", confidence)
    """
    # ensure scheme
    url = raw_url.strip()
    if not url.lower().startswith(("http://", "https://")):
        url = "http://" + url

    # whitelist check
    dom = urlparse(url.lower()).netloc.removeprefix("www.")
    if dom in WHITELIST:
        return "Legitimate", 1.0

    # ML inference
    inputs = _preprocess(raw_url)
    prob = float(MODEL.predict(inputs, verbose=0)[0, 0])
    if prob >= 0.5:
        return "Phishing", round(prob, 3)
    return "Legitimate", round(1.0 - prob, 3)

# ─────────────────────── CLI smoke-test ─────────────────────────
if __name__ == "__main__":
    import argparse, json as _j
    parser = argparse.ArgumentParser(
        description="Test URL-phishing model"
    )
    parser.add_argument("url", nargs="?", default="https://example.com")
    args = parser.parse_args()
    result = predict(args.url)
    print(_j.dumps({"url": args.url, "verdict": result[0], "confidence": result[1]}, indent=2))
