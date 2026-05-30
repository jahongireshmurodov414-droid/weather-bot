import logging
import asyncio
from datetime import datetime, timedelta

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes
)
from telegram.constants import ParseMode

from config import TELEGRAM_TOKEN
from database import (
    init_db, save_user, get_user, set_subscription, get_subscribers,
    add_note, get_notes, delete_note, add_reminder,
    get_pending_reminders, mark_reminder_sent
)
from weather import get_weather, get_weather_by_coords, get_forecast
from facts import get_today_facts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── KEYBOARDS ───────────────────────────────────────

def main_keyboard():
    return ReplyKeyboardMarkup([
        ["🌤 Погода", "📅 Прогноз на 5 дней"],
        ["📍 Моя погода", "📆 Факты дня"],
        ["📝 Заметки", "⚙️ Настройки"],
    ], resize_keyboard=True)

def notes_keyboard():
    return ReplyKeyboardMarkup([
        ["📋 Мои заметки", "🗑 Удалить заметку"],
        ["⏰ Напоминание", "🔙 Назад"],
    ], resize_keyboard=True)

def settings_keyboard():
    return ReplyKeyboardMarkup([
        ["🔔 Подписаться на рассылку", "🔕 Отписаться"],
        ["🏙 Сменить город", "🔙 Назад"],
    ], resize_keyboard=True)

def location_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📍 Отправить геолокацию", request_location=True)],
        ["🔙 Назад"],
    ], resize_keyboard=True)

# ─── START ───────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await save_user(user.id)
    await update.message.reply_text(
        f"👋 Привет, *{user.first_name}*!\n\n"
        "Я твой персональный помощник:\n"
        "🌤 Погода в любом городе\n"
        "📅 Прогноз на 5 дней\n"
        "📆 Факты и праздники дня\n"
        "📝 Заметки с напоминаниями\n\n"
        "Выбери что тебя интересует 👇",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=main_keyboard()
    )

# ─── WEATHER ─────────────────────────────────────────

async def weather_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        city = " ".join(context.args)
        await save_user(update.effective_user.id, city)
        res = await get_weather(city)
        await update.message.reply_text(res, parse_mode=ParseMode.MARKDOWN)
    else:
        context.user_data["action"] = "weather"
        await update.message.reply_text("🏙 Напиши название города:")

async def forecast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        city = " ".join(context.args)
        res = await get_forecast(city)
        await update.message.reply_text(res, parse_mode=ParseMode.MARKDOWN)
    else:
        context.user_data["action"] = "forecast"
        await update.message.reply_text("🏙 Напиши название города для прогноза:")

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = update.message.location
    result = await get_weather_by_coords(loc.latitude, loc.longitude)
    await update.message.reply_text(result, parse_mode=ParseMode.MARKDOWN, reply_markup=main_keyboard())

# ─── FACTS ───────────────────────────────────────────

async def today_facts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Загружаю факты дня...")
    res = await get_today_facts()
    await update.message.reply_text(res, parse_mode=ParseMode.MARKDOWN)

# ─── NOTES ───────────────────────────────────────────

async def notes_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["section"] = "notes"
    await update.message.reply_text(
        "📝 *Раздел заметок*\n\n"
        "Просто напиши текст, отправь 📸 фото или 🎤 голосовое — сохраню!\n\n"
        "Или выбери действие 👇",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=notes_keyboard()
    )

async def show_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    notes = await get_notes(update.effective_user.id)
    if not notes:
        await update.message.reply_text("📭 У тебя пока нет заметок.")
        return
    text = "📋 *Твои заметки:*\n\n"
    for note in notes:
        note_id, note_text, photo_id, voice_id, created_at = note
        date = created_at[:16]
        if note_text:
            preview = note_text[:60] + "..." if len(note_text) > 60 else note_text
            text += f"*#{note_id}* `{date}`\n📄 {preview}\n\n"
        elif photo_id:
            text += f"*#{note_id}* `{date}`\n📸 Фото\n\n"
        elif voice_id:
            text += f"*#{note_id}* `{date}`\n🎤 Голосовая заметка\n\n"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def note_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        text = " ".join(context.args)
        await add_note(update.effective_user.id, text=text)
        await update.message.reply_text("✅ Заметка сохранена!")
    else:
        await update.message.reply_text(
            "📝 Напиши текст после команды:\n`/note Текст заметки`",
            parse_mode=ParseMode.MARKDOWN
        )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_id = update.message.photo[-1].file_id
    caption = update.message.caption or None
    await add_note(update.effective_user.id, text=caption, photo_id=photo_id)
    await update.message.reply_text("📸 Фото сохранено как заметка!")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice_id = update.message.voice.file_id
    await add_note(update.effective_user.id, voice_id=voice_id)
    await update.message.reply_text("🎤 Голосовая заметка сохранена!")

# ─── SUBSCRIPTION ────────────────────────────────────

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = await get_user(user_id)
    city = user[1] if user else None
    if not city:
        context.user_data["action"] = "subscribe_city"
        await update.message.reply_text("🏙 Укажи свой город для утренней рассылки:")
        return
    await set_subscription(user_id, True)
    await update.message.reply_text(
        f"🔔 Подписка оформлена!\nКаждое утро в *9:00* получишь погоду + факты дня 🌅",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=main_keyboard()
    )

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await set_subscription(update.effective_user.id, False)
    await update.message.reply_text("🔕 Ты отписался от утренней рассылки.", reply_markup=main_keyboard())

# ─── MESSAGE HANDLER ─────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    action = context.user_data.get("action")
    section = context.user_data.get("section")

    if text == "🌤 Погода":
        context.user_data["action"] = "weather"
        return await update.message.reply_text("🏙 Напиши название города:")
    if text == "📅 Прогноз на 5 дней":
        context.user_data["action"] = "forecast"
        return await update.message.reply_text("🏙 Напиши название города для прогноза:")
    if text == "📍 Моя погода":
        return await update.message.reply_text("📍 Нажми кнопку ниже:", reply_markup=location_keyboard())
    if text == "📆 Факты дня":
        return await today_facts(update, context)
    if text == "📝 Заметки":
        return await notes_menu(update, context)
    if text == "⚙️ Настройки":
        return await update.message.reply_text("⚙️ *Настройки*", parse_mode=ParseMode.MARKDOWN, reply_markup=settings_keyboard())
    if text == "📋 Мои заметки":
        return await show_notes(update, context)
    if text == "🗑 Удалить заметку":
        context.user_data["action"] = "delete_note"
        return await update.message.reply_text("🗑 Напиши номер заметки для удаления:", parse_mode=ParseMode.MARKDOWN)
    if text == "⏰ Напоминание":
        context.user_data["action"] = "reminder"
        return await update.message.reply_text(
            "⏰ Напиши напоминание в формате:\n`Текст | 14:30`",
            parse_mode=ParseMode.MARKDOWN
        )
    if text == "🔔 Подписаться на рассылку":
        return await subscribe(update, context)
    if text == "🔕 Отписаться":
        return await unsubscribe(update, context)
    if text == "🏙 Сменить город":
        context.user_data["action"] = "change_city"
        return await update.message.reply_text("🏙 Напиши новый город:")
    if text == "🔙 Назад":
        context.user_data.clear()
        return await update.message.reply_text("Главное меню 👇", reply_markup=main_keyboard())

    if action == "weather":
        context.user_data.pop("action", None)
        await save_user(update.effective_user.id, text)
        res = await get_weather(text)
        await update.message.reply_text(res, parse_mode=ParseMode.MARKDOWN)
    elif action == "forecast":
        context.user_data.pop("action", None)
        res = await get_forecast(text)
        await update.message.reply_text(res, parse_mode=ParseMode.MARKDOWN)
    elif action == "delete_note":
        context.user_data.pop("action", None)
        try:
            note_id = int(text.strip())
            await delete_note(update.effective_user.id, note_id)
            await update.message.reply_text(f"✅ Заметка #{note_id} удалена.", reply_markup=notes_keyboard())
        except ValueError:
            await update.message.reply_text("❌ Напиши только номер, например: 3")
    elif action == "reminder":
        context.user_data.pop("action", None)
        try:
            parts = text.split("|")
            reminder_text = parts[0].strip()
            time_str = parts[1].strip()
            hour, minute = map(int, time_str.split(":"))
            now = datetime.now()
            remind_at = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if remind_at <= now:
                remind_at += timedelta(days=1)
            await add_reminder(update.effective_user.id, reminder_text, remind_at.strftime("%Y-%m-%d %H:%M:%S"))
            await update.message.reply_text(
                f"✅ Напоминание установлено!\n🔔 *{reminder_text}*\nВ {time_str}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=notes_keyboard()
            )
        except Exception:
            await update.message.reply_text("❌ Используй формат:\n`Текст | 14:30`", parse_mode=ParseMode.MARKDOWN)
    elif action == "subscribe_city":
        context.user_data.pop("action", None)
        await save_user(update.effective_user.id, text)
        await set_subscription(update.effective_user.id, True)
        await update.message.reply_text(
            f"🔔 Подписка оформлена! Каждое утро в *9:00* пришлю погоду в *{text}* + факты дня 🌅",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=main_keyboard()
        )
    elif action == "change_city":
        context.user_data.pop("action", None)
        await save_user(update.effective_user.id, text)
        await update.message.reply_text(f"✅ Город изменён на *{text}*", parse_mode=ParseMode.MARKDOWN, reply_markup=main_keyboard())
    elif section == "notes":
        await add_note(update.effective_user.id, text=text)
        await update.message.reply_text("✅ Заметка сохранена!", reply_markup=notes_keyboard())
    else:
        await update.message.reply_text("Используй меню 👇", reply_markup=main_keyboard())

# ─── SCHEDULER JOBS ──────────────────────────────────

async def morning_broadcast(context: ContextTypes.DEFAULT_TYPE):
    subscribers = await get_subscribers()
    facts = await get_today_facts()
    for user_id, city in subscribers:
        try:
            weather = await get_weather(city) if city else "🏙 Установи город в настройках"
            msg = f"🌅 *Доброе утро!*\n\n{weather}\n\n{'─'*22}\n\n{facts}"
            await context.bot.send_message(user_id, msg, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"Broadcast error {user_id}: {e}")

async def check_reminders(context: ContextTypes.DEFAULT_TYPE):
    reminders = await get_pending_reminders()
    for r_id, user_id, text in reminders:
        try:
            await context.bot.send_message(user_id, f"🔔 *Напоминание:*\n{text}", parse_mode=ParseMode.MARKDOWN)
            await mark_reminder_sent(r_id)
        except Exception as e:
            logger.error(f"Reminder error: {e}")

# ─── MAIN ─────────────────────────────────────────────

async def main():
    await init_db()
    logger.info("Database initialized")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("weather", weather_cmd))
    app.add_handler(CommandHandler("forecast", forecast_cmd))
    app.add_handler(CommandHandler("today", today_facts))
    app.add_handler(CommandHandler("note", note_cmd))
    app.add_handler(CommandHandler("notes", show_notes))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe))

    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    job_queue = app.job_queue
    job_queue.run_daily(morning_broadcast, time=datetime.strptime("09:00", "%H:%M").time())
    job_queue.run_repeating(check_reminders, interval=60)

    logger.info("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
