import json, os, logging
import azure.functions as func
import joblib
import pandas as pd

REQUIRED = ["Severity", "Status", "ClassificationReason", "Owner"]

# Load once (cold start)
MODEL = None
MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models", "incident_classifier.pkl"))
try:
    MODEL = joblib.load(MODEL_PATH)
    logging.info("✅ Model loaded")
except Exception as e:
    logging.error(f"❌ Model load failed: {e}")

def encode(df: pd.DataFrame) -> pd.DataFrame:
    # simple, model-agnostic encoding
    for c in REQUIRED:
        df[c] = df[c].astype(str).astype("category").cat.codes
    return df

def main(req: func.HttpRequest) -> func.HttpResponse:
    if MODEL is None:
        return func.HttpResponse(json.dumps({"error": "Model not loaded"}), status_code=500, mimetype="application/json")

    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse(json.dumps({"error": "No JSON body"}), status_code=400, mimetype="application/json")

    rows = body if isinstance(body, list) else [body]

    # validate & normalize
    clean = []
    for r in rows:
        missing = [k for k in REQUIRED if k not in r or r[k] is None]
        if missing:
            return func.HttpResponse(json.dumps({"error": f"Missing keys: {', '.join(missing)}"}),
                                     status_code=400, mimetype="application/json")
        clean.append({k: str(r[k]) for k in REQUIRED})

    df = pd.DataFrame(clean)
    df = encode(df)

    # predict
    if hasattr(MODEL, "predict_proba"):
        probs = MODEL.predict_proba(df)[:, 1]
    else:
        preds = MODEL.predict(df)
        import numpy as np
        probs = preds if isinstance(preds, (list, tuple)) else np.asarray(preds, dtype=float)

    out = []
    for p in probs:
        band = "High" if p >= 0.8 else ("Medium" if p >= 0.6 else "Low")
        pred = 1 if p >= 0.6 else 0
        out.append({"priority_score": float(p), "priority_band": band, "predicted_label": int(pred)})

    return func.HttpResponse(json.dumps(out[0] if isinstance(body, dict) else out),
                             status_code=200, mimetype="application/json")
