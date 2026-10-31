# Import packages
import os
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, Header, Request, status
from fastapi.responses import PlainTextResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

load_dotenv(override=True)

from agents.email_agent import analyze_email
from connectors.nylas_connector import event_to_email, store_raw_event, verify_signature
from schemas.nylas_webhook_schema import WebhookEvent
from services.email_service import EmailService

service = EmailService(analyze=analyze_email)

# Create the FastAPI app
app = FastAPI()

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")


# Read and insert webhook data
@app.api_route("/events", methods=["GET", "POST"])
async def webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_nylas_signature: Optional[str] = Header(None),
):
    if request.method == "GET":
        challenge = request.query_params.get("challenge")
        if challenge:
            print(" * Nylas connected to the webhook!")
            return PlainTextResponse(challenge)
        return PlainTextResponse(
            "No challenge", status_code=status.HTTP_400_BAD_REQUEST
        )
    # POST method
    body = await request.body()
    if not verify_signature(body, x_nylas_signature, os.environ.get("WEBHOOK_SECRET", "")):
        return PlainTextResponse("Signature verification failed!", status_code=401)

    # Store the raw event first, so nothing is lost if mapping fails
    store_raw_event(body)

    try:
        email = event_to_email(WebhookEvent.model_validate_json(body))
    except Exception as e:
        # Return 200 anyway: the raw event is saved, and a retry would fail the same way
        print(f" * Could not map event to Email: {type(e).__name__}: {e}")
        return PlainTextResponse("Event stored, mapping failed", status_code=200)

    # Enrich after the response is sent, so Nylas isn't kept waiting on the LLM
    if email and service.capture(email):
        background_tasks.add_task(service.enrich, email.id)
    return PlainTextResponse("Webhook received", status_code=200)


# Main page
@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        request, "index.html", {"records": service.list_emails()}
    )


# Run our application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
