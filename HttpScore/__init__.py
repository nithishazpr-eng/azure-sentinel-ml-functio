import logging
import json
import azure.functions as func
import joblib
import pandas as pd
import os

# Load model once on cold start
MODEL = None
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "incident_classifier.pkl")

try:
    MODEL = joblib.load(MODEL_PATH)
    logging.info("  Model loaded successfully")
except Exception as e:
    logging.error(f"  Failed to load model: {e}")

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(" HttpScore function triggered")

    if MODEL is None:
        return func.HttpResponse(
            json.dumps({"error": "Model not loaded on server"}),
            status_code=500,
            mimetype="application/json"
        )

    try:
        # Read JSON body
        body = req.get_json()
        logging.info(f"  Input received: {body}")

        # Convert to DataFrame (expects dict or list of dicts)
        if isinstance(body, dict):
            df = pd.DataFrame([body])
        else:
            df = pd.DataFrame(body)

        # Run prediction
        prediction = MODEL.predict(df)
        logging.info(f"  Prediction: {prediction.tolist()}")

        return func.HttpResponse(
            json.dumps({
                "ok": True,
                "prediction": prediction.tolist(),
                "input": body
            }),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f" Error while scoring: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
