import requests
from datetime import datetime

def get_today_facts() -> str:
    now = datetime.now()
    month = now.month
    day = now.day
    date_str = now.strftime("%d %B")

    lines = [f"📆 *Сегодня {date_str}*\n{'─' * 22}"]

    # ── 1. Праздники (Nager.Date) ──────────────────────
    try:
        r = requests.get(
            f"https://date.nager.at/api/v3/PublicHolidays/{now.year}/RU",
            timeout=8
        )
        if r.status_code == 200:
            holidays = [h for h in r.json() if h["date"][5:] == now.strftime("%m-%d")]
            if holidays:
                lines.append("📅 *Праздники сегодня:*")
                for h in holidays[:3]:
                    lines.append(f"• {h['localName']}")
            else:
                lines.append("📅 Государственных праздников сегодня нет")
    except Exception:
        lines.append("📅 Праздники недоступны")

    lines.append("")

    # ── 2. События в истории (Wikipedia) ──────────────
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}",
            timeout=8
        )
        if r.status_code == 200:
            events = r.json().get("events", [])[:3]
            if events:
                lines.append("🌍 *В этот день в истории:*")
                for e in events:
                    year = e.get("year", "")
                    text = e.get("text", "")
                    if len(text) > 80:
                        text = text[:80] + "..."
                    lines.append(f"• {year} — {text}")
    except Exception:
        lines.append("🌍 История недоступна")

    lines.append("")

    # ── 3. Интересный факт (Numbers API) ──────────────
    try:
        r = requests.get(
            f"http://numbersapi.com/{month}/{day}/date",
            timeout=8
        )
        if r.status_code == 200:
            lines.append(f"🔬 *Интересный факт:*\n• {r.text}")
    except Exception:
        lines.append("🔬 Факт дня недоступен")

    return "\n".join(lines)
