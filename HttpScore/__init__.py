import azure.functions as func
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
    except:
        body = {}

    return func.HttpResponse(
        json.dumps({"ok": True, "received": body}),
        status_code=200,
        mimetype="application/json"
    )
