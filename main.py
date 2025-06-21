import uuid
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import jwt

app = FastAPI()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_API_KEY = os.environ.get("SUPABASE_API_KEY")
SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET")  # 必要に応じて設定

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ikechanpan.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_jwt_token(token: str):
    try:
        print("Verifying token...")
        print("Using SUPABASE_JWT_SECRET:", repr(SUPABASE_JWT_SECRET)[:10], "...")  # 一部だけ表示
        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"])
        print("JWT payload decoded successfully:", payload)
        return payload
    except jwt.ExpiredSignatureError:
        print("JWT decode failed: Token has expired")
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        print("JWT decode failed:", str(e))
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/save") 
async def save_to_supabase(request: Request, authorization: str = Header(None)):

    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    token = authorization.replace("Bearer ", "")
    print("Authorization header:", authorization)
    print("Extracted token:", token[:30])

    verify_jwt_token(token)

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
