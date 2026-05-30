import os
import logging
from dotenv import load_dotenv

# Настройка логирования для конфига
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
OPENWEATHER_KEY = os.environ.get("OPENWEATHER_KEY", "")

# Проверка на плейсхолдеры или пустые значения
PLACEHOLDERS = ["ВАШ_ТЕЛЕГРАМ_ТОКЕН", "ВАШ_КЛЮЧ_ПОГОДЫ", ""]

if TELEGRAM_TOKEN in PLACEHOLDERS:
    logger.error("❌ ОШИБКА: TELEGRAM_TOKEN не установлен или содержит значение по умолчанию в .env!")
    TELEGRAM_TOKEN = None

if OPENWEATHER_KEY in PLACEHOLDERS:
    logger.warning("⚠️ ПРЕДУПРЕЖДЕНИЕ: OPENWEATHER_KEY не установлен. Функции погоды не будут работать.")
    OPENWEATHER_KEY = None
