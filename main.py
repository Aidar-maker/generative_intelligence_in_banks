from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from llm_client import generate_survey_from_journey

app = FastAPI(title="Uralsib Survey Gen")

# Разрешаем запросы с фронтенда (наш HTML файл)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RequestBody(BaseModel):
    journey: str
    hint: Optional[str] = None


@app.post("/api/generate")
def api_generate(data: RequestBody):
    if not data.journey.strip():
        raise HTTPException(status_code=400, detail="Путь не может быть пустым")

    result = generate_survey_from_journey(data.journey, data.hint)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


if __name__ == "__main__":
    # Запуск сервера на порту 8000
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)