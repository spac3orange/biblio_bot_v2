import gspread
from oauth2client.service_account import ServiceAccountCredentials

KEY_FILE = 'config/my-project-library-435708-2461a1714d4d.json'

# Установите ваши права доступа и используйте их для авторизации
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE, scope)
client = gspread.authorize(credentials)

# Откройте таблицу по названию
spreadsheet = client.open("books_lib_table")

# Выберите лист
worksheet = spreadsheet.sheet1


async def get_sheet_data():
    # Получите все данные из таблицы
    data = worksheet.get_all_records()
    return data

