# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Any
import sqlite3
import uvicorn

from llm_client import generate_survey_from_journey  # Твой существующий клиент
from prompts import SYSTEM_PROMPT  # Твой существующий промпт
import database as db  # Новый модуль

app = FastAPI(title="Bank Survey Generator MVP")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем любые источники
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем любые методы (GET, POST и т.д.)
    allow_headers=["*"],  # Разрешаем любые заголовки
)

# Инициализация БД при старте
@app.on_event("startup")
def startup_event():
    db.init_db()


class SurveyRequest(BaseModel):
    journey: Any  # Может быть строкой или объектом
    hint: Optional[str] = None


class SurveyResponse(BaseModel):
    category: str
    relevance: float
    questions: List[str]


# --- Существующий эндпоинт (обновленный) ---
@app.post("/api/generate", response_model=SurveyResponse)
async def generate_survey(request: SurveyRequest):
    # Вызов модели
    result = generate_survey_from_journey(request.journey, request.hint)

    # Сохранение в БД (асинхронно или в фоне, здесь синхронно для простоты)
    db.save_survey(
        journey=request.journey,
        hint=request.hint,
        result=result,
        prompt=SYSTEM_PROMPT,
        model_name="meta-llama-3.1-8b-instruct"
    )

    return result


# --- Новые эндпоинты для истории ---

@app.get("/api/surveys")
async def list_surveys(limit: int = 50):
    """Получить список последних сгенерированных опросов."""
    return db.get_all_surveys(limit)


@app.get("/api/surveys/{survey_id}")
async def get_survey(survey_id: int):
    """Получить детали конкретного опроса."""
    # Простая реализация через прямой запрос, можно вынести в database.py
    with sqlite3.connect(db.DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM surveys WHERE id = ?", (survey_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Survey not found")
        return dict(row)


from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Монтируем в конец, чтобы не перекрывать API-роуты
app.mount("/", StaticFiles(directory=str(Path(__file__).parent / "frontend"), html=True), name="frontend")

if __name__ == "__main__":
    # Запуск сервера на порту 8000
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)