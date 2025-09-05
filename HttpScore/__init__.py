import json, os
import azure.functions as func
import joblib
import pandas as pd

# Load model once (cold start)
MODEL = None
FEATURES = ["Severity","Status","ClassificationReason","Owner"]

def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    # same encoding approach used during training:
    # LabelEncoder was fitted per-column; here we mimic with categorical type then codes.
    # For production you’d persist encoders; for demo we use type codes safely.
    for col in FEATURES:
        df[col] = df[col].astype(str).astype("category").cat.codes
    return df

def load_model():
    global MODEL
    if MODEL is None:
        base = os.path.dirname(__file__)
        model_path = os.path.join(base, "..", "models", "incident_classifier.pkl")
        MODEL = joblib.load(model_path)
    return MODEL

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
        # Expect either a single incident or an array
        items = body if isinstance(body, list) else [body]

        rows = []
        for itm in items:
            row = {k: itm.get(k) for k in FEATURES}
            rows.append(row)

        df = pd.DataFrame(rows)
        df = encode_categoricals(df)

        model = load_model()
        probs = model.predict_proba(df)[:,1]  # probability of TruePositive
        preds = (probs >= 0.6).astype(int)    # threshold 0.6 (tune later)

        out = []
        for p, pr in zip(preds, probs):
            band = "High" if pr>=0.8 else ("Medium" if pr>=0.6 else "Low")
            out.append({
                "priority_score": float(pr),
                "priority_band": band,
                "predicted_label": int(p)  # 1=TruePositive
            })

        return func.HttpResponse(
            json.dumps(out[0] if isinstance(body, dict) else out),
            status_code=200, mimetype="application/json"
        )
    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)
