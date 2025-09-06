import os, json, logging
import azure.functions as func

INFO = {}

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        base = os.path.dirname(__file__)  # .../site/wwwroot/HttpScore
        model_path = os.path.abspath(os.path.join(base, "..", "models", "incident_classifier.pkl"))
        INFO["cwd"] = os.getcwd()
        INFO["__file__"] = __file__
        INFO["model_path"] = model_path
        INFO["model_exists"] = os.path.exists(model_path)

        # try loading with joblib only if file exists
        if INFO["model_exists"]:
            try:
                import joblib
                m = joblib.load(model_path)
                INFO["model_loaded"] = True
                INFO["model_type"] = str(type(m))
            except Exception as e:
                INFO["model_loaded"] = False
                INFO["load_error"] = f"{type(e).__name__}: {e}"
        else:
            INFO["model_loaded"] = False
            INFO["load_error"] = "Model file not found"

        return func.HttpResponse(json.dumps(INFO), status_code=200, mimetype="application/json")

    except Exception as e:
        return func.HttpResponse(json.dumps({"fatal": f"{type(e).__name__}: {e}", "debug": INFO}),
                                 status_code=500, mimetype="application/json")
