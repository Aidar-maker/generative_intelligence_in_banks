import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "surveys.db"

def init_db():
    # создаем таблицу, если ее нет
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS surveys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                client_journey TEXT NOT NULL,
                hint TEXT,
                generated_result TEXT NOT NULL,
                prompt_used TEXT,
                user_edited_result TEXT,
                model_name TEXT
            )
        """)
        conn.commit()

def save_survey(journey, hint, result, prompt=None, edited_result=None, model_name=None):
    # пишем опрос в базу. результат сериализуем в json
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO surveys (
                client_journey, hint, generated_result, prompt_used, user_edited_result, model_name
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            json.dumps(journey, ensure_ascii=False) if isinstance(journey, dict) else journey,
            hint,
            json.dumps(result, ensure_ascii=False),
            prompt,
            json.dumps(edited_result, ensure_ascii=False) if edited_result else None,
            model_name
        ))
        conn.commit()
        return cursor.lastrowid

def get_all_surveys(limit=50):
    # берем последние опросы, сортируем по дате
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM surveys ORDER BY created_at DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]