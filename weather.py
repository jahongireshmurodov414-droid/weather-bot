import requests
from datetime import datetime
from config import OPENWEATHER_KEY

BASE_URL = "https://api.openweathermap.org/data/2.5"

EMOJI_MAP = {
    "Clear": "☀️", "Clouds": "☁️", "Rain": "🌧️",
    "Drizzle": "🌦️", "Thunderstorm": "⛈️", "Snow": "❄️",
    "Mist": "🌫️", "Fog": "🌫️", "Haze": "🌫️", "Smoke": "🌫️",
}

WIND_DIR = ["С", "СВ", "В", "ЮВ", "Ю", "ЮЗ", "З", "СЗ"]

def wind_direction(deg):
    return WIND_DIR[round(deg / 45) % 8]

def time_emoji(hour):
    if 6 <= hour < 12: return "🌅"
    if 12 <= hour < 18: return "☀️"
    if 18 <= hour < 22: return "🌆"
    return "🌙"

def get_weather(city: str) -> str:
    params = {"q": city, "appid": OPENWEATHER_KEY, "units": "metric", "lang": "ru"}
    try:
        r = requests.get(f"{BASE_URL}/weather", params=params, timeout=10)
        if r.status_code == 404:
            return f"❌ Город *{city}* не найден. Проверь название."
        if r.status_code != 200:
            return "⚠️ Ошибка при получении погоды. Попробуй позже."
        d = r.json()
        return _format_current(d)
    except Exception as e:
        return f"❌ Ошибка: {e}"

def get_weather_by_coords(lat: float, lon: float) -> str:
    params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_KEY, "units": "metric", "lang": "ru"}
    try:
        r = requests.get(f"{BASE_URL}/weather", params=params, timeout=10)
        if r.status_code != 200:
            return "⚠️ Не удалось получить погоду по геолокации."
        return _format_current(r.json())
    except Exception as e:
        return f"❌ Ошибка: {e}"

def get_forecast(city: str) -> str:
    params = {"q": city, "appid": OPENWEATHER_KEY, "units": "metric", "lang": "ru", "cnt": 40}
    try:
        r = requests.get(f"{BASE_URL}/forecast", params=params, timeout=10)
        if r.status_code == 404:
            return f"❌ Город *{city}* не найден."
        if r.status_code != 200:
            return "⚠️ Ошибка при получении прогноза."
        return _format_forecast(r.json())
    except Exception as e:
        return f"❌ Ошибка: {e}"

def _format_current(d: dict) -> str:
    main = d["weather"][0]["main"]
    emoji = EMOJI_MAP.get(main, "🌡️")
    desc = d["weather"][0]["description"].capitalize()
    temp = round(d["main"]["temp"])
    feels = round(d["main"]["feels_like"])
    humidity = d["main"]["humidity"]
    wind = round(d["wind"]["speed"])
    wind_deg = d["wind"].get("deg", 0)
    wind_dir = wind_direction(wind_deg)
    city = d["name"]
    country = d["sys"]["country"]
    hour = datetime.utcfromtimestamp(d["dt"]).hour + d.get("timezone", 0) // 3600
    t_emoji = time_emoji(hour % 24)
    rain = d.get("rain", {}).get("1h", 0)
    rain_text = f"🌧 Осадки: {rain} мм/ч" if rain else "🌂 Осадков не ожидается"

    return (
        f"{t_emoji} *{city}, {country}*\n"
        f"{'─' * 22}\n"
        f"{emoji} *{temp}°C* · {desc}\n\n"
        f"😌 Ощущается как *{feels}°C*\n"
        f"💧 Влажность: *{humidity}%*\n"
        f"💨 Ветер: *{wind} м/с* · {wind_dir}\n"
        f"{rain_text}"
    )

def _format_forecast(d: dict) -> str:
    city = d["city"]["name"]
    country = d["city"]["country"]
    lines = [f"📅 *Прогноз на 5 дней · {city}, {country}*\n{'─' * 22}"]

    days = {}
    for item in d["list"]:
        date = item["dt_txt"][:10]
        if date not in days:
            days[date] = []
        days[date].append(item)

    for date, items in list(days.items())[:5]:
        temps = [i["main"]["temp"] for i in items]
        main = items[len(items)//2]["weather"][0]["main"]
        desc = items[len(items)//2]["weather"][0]["description"].capitalize()
        emoji = EMOJI_MAP.get(main, "🌡️")
        t_min = round(min(temps))
        t_max = round(max(temps))
        weekday = datetime.strptime(date, "%Y-%m-%d").strftime("%a %d.%m")
        lines.append(f"{emoji} *{weekday}* · {t_min}° / {t_max}° · {desc}")

    # Почасовой на сегодня
    lines.append(f"\n⏰ *Сегодня по часам:*")
    today_items = list(days.values())[0][:4]
    hour_line = ""
    temp_line = ""
    for item in today_items:
        hour = item["dt_txt"][11:16]
        temp = round(item["main"]["temp"])
        main = item["weather"][0]["main"]
        em = EMOJI_MAP.get(main, "🌡️")
        hour_line += f"{hour}  "
        temp_line += f"{em}{temp}°  "
    lines.append(hour_line)
    lines.append(temp_line)

    return "\n".join(lines)
