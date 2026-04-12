import requests
import json
from prompts import SYSTEM_PROMPT

# URL локального сервера LM Studio
API_URL = "http://localhost:1234/v1/chat/completions"
MODEL_NAME = "meta-llama-3.1-8b-instruct"


def generate_survey_from_journey(journey_text: str, hint: str = None):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Путь клиента: {journey_text}\nПодсказка: {hint}"}
        ],
        "temperature": 0.1,  # Для строгого JSON
        "max_tokens": 500,
        "response_format": {"type": "json_object"}
    }

    try:
        # Постучались в LM Studio
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()

        raw_content = response.json()["choices"][0]["message"]["content"]

        # Иногда модель добавляет маркдаун ```json ... ```, режем его
        raw_content = raw_content.replace("```json", "").replace("```", "").strip()

        return json.loads(raw_content)

    except requests.exceptions.ConnectionError:
        return {"error": "LM Studio не запущен или недоступен"}
    except Exception as e:
        return {"error": f"Ошибка обработки: {str(e)}"}