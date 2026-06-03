from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Any
from pathlib import Path
import sqlite3
import uvicorn

import database as db
from llm_client import generate_survey_from_journey
from prompts import SYSTEM_PROMPT

app = FastAPI(title="Bank Survey Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    db.init_db()

class SurveyRequest(BaseModel):
    journey: Any
    hint: Optional[str] = None

class SurveyResponse(BaseModel):
    category: str
    relevance: float
    questions: List[str]

@app.post("/api/generate", response_model=SurveyResponse)
async def generate_survey(request: SurveyRequest):
    result = generate_survey_from_journey(request.journey, request.hint)

    # сохраняем в историю
    db.save_survey(
        journey=request.journey,
        hint=request.hint,
        result=result,
        prompt=SYSTEM_PROMPT,
        model_name="meta-llama-3.1-8b-instruct"
    )
    return result

@app.get("/api/surveys")
async def list_surveys(limit: int = 50):
    return db.get_all_surveys(limit)

@app.get("/api/surveys/{survey_id}")
async def get_survey(survey_id: int):
    # тащим конкретный опрос по id
    with sqlite3.connect(db.DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM surveys WHERE id = ?", (survey_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Опрос не найден")
        return dict(row)

app.mount("/", StaticFiles(directory=str(Path(__file__).parent / "frontend"), html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)