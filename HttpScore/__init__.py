import logging
import azure.functions as func
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    try:
        body = req.get_json()
    except ValueError:
        body = {"note": "No JSON body received"}

    return func.HttpResponse(
        json.dumps({"ok": True, "received": body}),
        status_code=200,import logging
import azure.functions as func
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    try:
        # Try to parse JSON body
        body = req.get_json()
    except ValueError:
        # If no JSON body is passed
        body = {"error": "No JSON body received"}

    return func.HttpResponse(
        json.dumps({
            "ok": True,
            "received": body
        }),
        status_code=200,
        mimetype="application/json"
    )

        mimetype="application/json"
    )
