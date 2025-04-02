import gspread
import json
import io
from datetime import datetime
from google.oauth2.service_account import Credentials
from config import GOOGLE_SHEET_ID, GOOGLE_CREDENTIALS_FILE

def get_sheet():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        # Парсим JSON из строки переменной окружения
        service_account_info = json.loads(GOOGLE_CREDENTIALS_FILE)
        creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet("база данных")
        return sheet
    except Exception as e:
        raise RuntimeError(f"Ошибка при получении листа Google Sheets: {e}")


async def append_data_to_sheet(phone, username, tg_id, user_id, order_number):
    try:
        sheet = get_sheet()
        now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        row = [phone, username, tg_id, user_id, order_number, now, ""]
        sheet.append_row(row)
    except Exception as e:
        raise RuntimeError(f"Ошибка при записи в Google Sheets: {e}")
