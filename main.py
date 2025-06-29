import uuid
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import jwt

app = FastAPI()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_API_KEY = os.environ.get("SUPABASE_API_KEY")
SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.moneygement\.pages\.dev",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"], audience="authenticated")
        print(payload)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        print("JWT decode failed:", str(e))
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/save")
async def save_to_supabase(request: Request, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    token = authorization.replace("Bearer ", "")
    payload = verify_jwt_token(token)

    data = await request.json()
    data["id"] = str(uuid.uuid4())
    data["user_id"] = payload["sub"]
    print("Data to insert:", data)
    
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
def get_expenses(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    token = authorization.replace("Bearer ", "")
    verify_jwt_token(token)

    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}"
    }

    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/expenses?select=*",
        headers=headers
    )

    return {"status": "fetched", "data": response.json()}
