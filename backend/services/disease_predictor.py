"""
ML disease classifier trained on the Symptom2Disease dataset.

Dataset: download Symptom2Disease.csv from
  https://www.kaggle.com/datasets/niyarrbarman/symptom2disease
Save it as:  backend/data/Symptom2Disease.csv

Columns expected: label, text
  label — disease name (string)
  text  — natural-language symptom description

On first startup the model trains (~10 s) and saves to backend/models/disease_clf.pkl.
Subsequent startups load the pickle instantly.
"""

import os
import pickle
import numpy as np
from pathlib import Path

_BASE = Path(__file__).resolve().parent.parent
MODEL_PATH = _BASE / "models" / "disease_clf.pkl"
DATA_PATH = _BASE / "data" / "Symptom2Disease.csv"

_pipeline = None
_available = False


def load_or_train_model() -> None:
    global _pipeline, _available

    if MODEL_PATH.exists():
        with open(MODEL_PATH, "rb") as fh:
            _pipeline = pickle.load(fh)
        _available = True
        print("[disease_predictor] Loaded classifier from cache.")
        return

    if not DATA_PATH.exists():
        print(
            f"[disease_predictor] Dataset not found at {DATA_PATH}. "
            "ML disease prediction disabled — download Symptom2Disease.csv from Kaggle."
        )
        return

    print("[disease_predictor] Training SVM classifier on Symptom2Disease dataset…")
    _pipeline = _train()
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MODEL_PATH, "wb") as fh:
        pickle.dump(_pipeline, fh)
    _available = True
    print("[disease_predictor] Classifier trained and saved.")


def _train():
    import pandas as pd
    from sklearn.pipeline import Pipeline
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.svm import SVC
    from sklearn.calibration import CalibratedClassifierCV

    df = pd.read_csv(DATA_PATH)
    # Tolerate minor column-name variations
    text_col = next((c for c in df.columns if c.lower() == "text"), df.columns[-1])
    label_col = next((c for c in df.columns if c.lower() == "label"), df.columns[0])

    X = df[text_col].fillna("").tolist()
    y = df[label_col].tolist()

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=15000,
            sublinear_tf=True,
            min_df=1,
        )),
        ("clf", CalibratedClassifierCV(
            SVC(kernel="linear", C=1.0, class_weight="balanced"),
            cv=3,
        )),
    ])
    pipeline.fit(X, y)
    return pipeline


def predict_disease(query_text: str, extracted_symptoms: list[str]) -> dict:
    """
    Predict most likely skin disease. Non-skin predictions from the dataset are filtered out.

    Returns a dict with disease, confidence, alternatives, ml_used flag.
    """
    if not _available or _pipeline is None:
        load_or_train_model()
    if not _available or _pipeline is None:
        return {"disease": None, "confidence": 0.0, "alternatives": [], "ml_used": False}

    from services.medical_kb import DISEASE_KB
    skin_diseases = set(DISEASE_KB.keys())

    text = f"{query_text} {' '.join(extracted_symptoms)}"
    proba: np.ndarray = _pipeline.predict_proba([text])[0]
    classes: np.ndarray = _pipeline.classes_

    # Check top 5 candidates, only keep skin conditions
    top_idx = np.argsort(proba)[::-1][:5]
    skin_preds = [
        (str(classes[i]), float(proba[i]))
        for i in top_idx
        if str(classes[i]) in skin_diseases
    ]

    if not skin_preds:
        return {"disease": None, "confidence": 0.0, "alternatives": [], "ml_used": True}

    top_disease, top_conf = skin_preds[0]
    alternatives = [
        {"disease": d, "confidence": round(c, 3)}
        for d, c in skin_preds[1:3]
        if c > 0.08
    ]

    return {
        "disease": top_disease,
        "confidence": round(top_conf, 3),
        "alternatives": alternatives,
        "ml_used": True,
    }


def model_available() -> bool:
    return _available
