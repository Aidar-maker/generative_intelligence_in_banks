import requests
import json
from prompts import SYSTEM_PROMPT

LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"


def generate_survey_from_journey(journey, hint=None):
    # собираем текст для модели
    if isinstance(journey, dict):
        journey_text = json.dumps(journey, ensure_ascii=False)
    else:
        journey_text = str(journey)

    user_msg = f"Путь клиента: {journey_text}"
    if hint:
        user_msg += f"\nПодсказка: {hint}"

    payload = {
        "model": "local-model",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg}
        ],
        "temperature": 0.3,
        "max_tokens": 1024,
        "stream": False
    }

    try:
        # стучимся в локальную студию
        resp = requests.post(LM_STUDIO_URL, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()

        content = data["choices"][0]["message"]["content"].strip()

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        return json.loads(content)

    except requests.exceptions.ConnectionError:
        raise ConnectionError("LM Studio не отвечает. Проверь, запущена ли она на 1234 порту")
    except requests.exceptions.Timeout:
        raise TimeoutError("Модель тупит, таймаут")
    except json.JSONDecodeError as e:
        # защита от невалидного json
        raise ValueError(f"Кривой JSON от модели: {content[:200]}... Ошибка: {e}")