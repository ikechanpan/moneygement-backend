from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # フロントのドメインに限定してもOK
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = "expenses.json"

@app.post("/save")
async def save_expense(request: Request):
    new_data = await request.json()

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            expenses = json.load(f)
    else:
        expenses = []

    expenses.append(new_data)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(expenses, f, ensure_ascii=False, indent=2)

    return {"status": "success", "data": new_data}
