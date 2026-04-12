# test_api.py
import json
from llm_client import generate_survey_from_journey

journ = {
    "steps": [
        "Открыл приложение",
        "Выбрал кредит",
        "Не завершил заявку"
    ]
}

result = generate_survey_from_journey(
    journey=json.dumps(journ, ensure_ascii=False),
    hint="акцент на причины отказа"
)

print(result)