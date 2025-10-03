# backend/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from twilio.rest import Client
import os
from dotenv import load_dotenv

# Load environment variables (for local development only)
load_dotenv()

# --- Configuration (FastAPI and Twilio) ---
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
TARGET_NUMBER = os.getenv("TARGET_MOBILE_NUMBER")

# Initialize Twilio client (will use environment variables if provided)
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

app = FastAPI(title="Red Light SMS Alert API")

# --- CORS Configuration ---
# IMPORTANT: This allows your frontend (hosted on a different domain/port) 
# to talk to your backend API.
origins = [
    "*", # For development; change to your specific frontend URL in production (e.g., "https://your-frontend.vercel.app")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request Body Model ---
class AlertMessage(BaseModel):
    message: str

# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"status": "API is running. POST to /alert to trigger SMS."}


@app.post("/alert")
async def send_sms_alert(data: AlertMessage):
    """
    Receives an alert signal from the client and sends an SMS via Twilio.
    """
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        raise HTTPException(status_code=500, detail="Server misconfigured: Twilio secrets missing.")

    try:
        twilio_client.messages.create(
            to=TARGET_NUMBER,
            from_=TWILIO_NUMBER,
            body=f"🚨 ALERT: Red LED detected! Message: {data.message}"
        )
        print(f"SMS Alert Sent to {TARGET_NUMBER}")
        return {"success": True, "message": "SMS sent successfully."}

    except Exception as e:
        print(f"Twilio API Error: {e}")
        # In production, avoid exposing full error details
        raise HTTPException(status_code=500, detail="Failed to send SMS via Twilio.")