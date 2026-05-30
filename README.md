# Telegram Personal Assistant Bot

Универсальный телеграм-бот помощник с функциями погоды, фактов дня, заметок и напоминаний.

## Основные возможности

- 🌤 **Погода:** Текущая погода в любом городе и прогноз на 5 дней.
- 📍 **Геолокация:** Получение погоды по вашему местоположению.
- 📆 **Факты дня:** Информация о праздниках, исторических событиях и интересные факты.
- 📝 **Заметки:** Сохранение текстовых, фото и голосовых заметок.
- ⏰ **Напоминания:** Установка напоминаний на определенное время.
- 🔔 **Рассылка:** Автоматическая утренняя рассылка с погодой и фактами.

## Технологии

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) — асинхронная библиотека для работы с Telegram API.
- [httpx](https://github.com/encode/httpx) — асинхронный HTTP клиент.
- [aiosqlite](https://github.com/omnilib/aiosqlite) — асинхронная библиотека для работы с SQLite.
- [OpenWeatherMap API](https://openweathermap.org/api) — данные о погоде.

## Установка и запуск

1. **Клонируйте репозиторий:**
   ```bash
   git clone <your_repository_url>
   cd <your_project_directory>
   ```

2. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Настройте переменные окружения:**
   Создайте файл `.env` в корневой директории и добавьте туда ваши токены:
   ```env
   TELEGRAM_TOKEN=ваш_токен_бота
   OPENWEATHER_KEY=ваш_ключ_openweathermap
   ```

4. **Запустите бота:**
   ```bash
   python bot.py
   ```

## Конфигурация

Бот использует `python-dotenv` для загрузки настроек. Обязательно получите `TELEGRAM_TOKEN` у [@BotFather](https://t.me/BotFather) и `OPENWEATHER_KEY` на сайте [OpenWeatherMap](https://home.openweathermap.org/api_keys).
