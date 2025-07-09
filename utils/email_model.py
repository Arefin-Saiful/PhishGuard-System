# utils/email_model.py
"""
End-to-end hybrid e-mail-phishing detector
──────────────────────────────────────────
Artifacts in models/email/ :
 • tokenizer.pkl      → turns body text into integer sequences
 • hybrid_model.h5    → single Keras model, Input(shape=(MAX_LEN,))
"""

from __future__ import annotations
import email, html, re, pickle, numpy as np, tensorflow as tf
from pathlib import Path

# ───────────────────────────── paths ──────────────────────────────
BASE   = Path(__file__).resolve().parents[1] / "models" / "email"
TOKENF = BASE / "tokenizer.pkl"
MODELF = BASE / "hybrid_model.h5"

# ───────────────────────── artefacts ──────────────────────────────
with TOKENF.open("rb") as fh:
    TOKENIZER = pickle.load(fh)                   # same tokenizer as training

MODEL_NET = tf.keras.models.load_model(MODELF)    # <Input shape=(None, MAX_LEN)>
MAX_LEN   = MODEL_NET.input_shape[1]              # e.g. 500

# ───────────────────────── helpers ────────────────────────────────
def _clean_body(msg_bytes: bytes) -> str:
    """
    Extract and normalise the plain-text body from raw .eml bytes.
    Returns a *single* lowercase string (no lists).
    """
    msg   = email.message_from_bytes(msg_bytes)
    parts: list[str] = []

    for part in msg.walk():
        if part.get_content_type() != "text/plain":
            continue
        payload = part.get_payload(decode=True)
        if not payload:
            continue
        charset = part.get_content_charset() or "utf-8"
        try:
            parts.append(payload.decode(charset, errors="ignore"))
        except LookupError:                       # unknown charset
            parts.append(payload.decode(errors="ignore"))

    # fall back to the root payload if no text/plain parts found
    if not parts and msg.get_payload():
        root_payload = msg.get_payload(decode=True)
        if isinstance(root_payload, (bytes, bytearray)):
            parts.append(root_payload.decode(errors="ignore"))

    text = " ".join(parts)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).lower().strip()
    return text

def _vectorise(text: str) -> np.ndarray:
    """Word-index sequence padded/truncated to MAX_LEN."""
    seq = TOKENIZER.texts_to_sequences([text])
    seq = tf.keras.preprocessing.sequence.pad_sequences(
            seq, maxlen=MAX_LEN, padding="post")
    return seq.astype("int32")

# ─────────────────────── public API ───────────────────────────────
def predict(raw_eml: bytes) -> tuple[str, float]:
    """
    Parameters
    ----------
    raw_eml : bytes   Raw .eml file uploaded by the user.

    Returns
    -------
    verdict     : "Phishing" | "Legitimate"
    confidence  : float – already aligned to the chosen class (0-1)
    """
    body = _clean_body(raw_eml)
    x    = _vectorise(body)

    prob = float(MODEL_NET.predict(x, verbose=0)[0, 0])  # phishing probability
    verdict = "Phishing" if prob >= 0.5 else "Legitimate"
    conf    = prob if verdict == "Phishing" else 1 - prob
    return verdict, round(conf, 3)

# ────────────────────── CLI self-test ─────────────────────────────
if __name__ == "__main__":
    import sys, json
    if len(sys.argv) != 2:
        print("Usage: python -m utils.email_model path/to/sample.eml")
        sys.exit(1)
    raw = Path(sys.argv[1]).read_bytes()
    v, c = predict(raw)
    print(json.dumps({"verdict": v, "confidence": c}, indent=2))
