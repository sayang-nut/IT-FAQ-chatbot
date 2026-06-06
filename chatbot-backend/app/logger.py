# app/logger.py
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_sheet():
    creds = Credentials.from_service_account_file(
        "service_account.json",
        scopes=SCOPES
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID"))
    return sheet.sheet1


def build_log_row(question: str, answer: str, results: list[dict]) -> list:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if results:
        top = results[0]
        category = top["item"]["category"]
        score = top["score"]
        escalated = "No"
    else:
        category = "Unknown"
        score = 0.0
        escalated = "Yes"  # không tìm được → phải escalate lên IT

    return [timestamp, question, answer, category, score, escalated]


async def log_conversation(question: str, answer: str, results: list[dict]):
    """
    Hàm async — được gọi như background task trong FastAPI.
    Ghi log không chặn response trả về cho user.
    """
    try:
        sheet = get_sheet()
        row = build_log_row(question, answer, results)
        sheet.append_row(row)
        print(f"[Logger] Logged: {row[0]} | {row[3]} | score={row[4]}")
    except Exception as e:
        # Log lỗi nhưng không crash server
        print(f"[Logger] Failed to log: {e}")