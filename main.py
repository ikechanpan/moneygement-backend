import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_API_KEY = os.environ.get("SUPABASE_API_KEY")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/save")
async def save_to_supabase(request: Request):
    data = await request.json()

    data["id"] = str(uuid.uuid4())

    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/expenses",
        headers=headers,
        json=[data]
    )

    print("Supabase response:", response.status_code, response.text)

    try:
        return {"status": "supabase_saved", "response": response.json()}
    except Exception:
        return {"status": "supabase_error", "response": response.text}

@app.get("/list")
def get_expenses():
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}"
    }

    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/expenses?select=*",
        headers=headers
    )

    return {"status": "fetched", "data": response.json()}
