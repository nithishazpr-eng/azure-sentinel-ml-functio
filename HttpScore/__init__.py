import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        "Hello from Azure Functions!",
        status_code=200
    )
