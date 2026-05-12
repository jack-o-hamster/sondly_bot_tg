import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_searches = {}

@dp.message(Command('start'))
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Поиск музыки", callback_data="search_music")]
    ])
    await message.answer("Привет! Я Sondly Bot 🎵\nНажми кнопку для поиска музыки.", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data == "search_music")
async def search_prompt(callback: types.CallbackQuery):
    await callback.message.answer("Введите название трека или исполнителя:")
    await callback.answer()

@dp.message()
async def search_music(message: types.Message):
    query = message.text.strip()
    if len(query) < 2:
        await message.answer("Запрос слишком короткий.")
        return

    await message.answer("🔍 Ищу треки, подожди...")

    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'default_search': 'ytsearch15',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(f"ytsearch15:{query}", download=False)

        if not result or not result.get('entries'):
            await message.answer("Ничего не найдено 😔")
            return

        entries = result['entries'][:15]
        user_searches[message.from_user.id] = entries

        text = f"🔎 Найдено: {len(entries)} треков\n\n"
        keyboard = []
        for i, entry in enumerate(entries):
            title = entry.get('title', 'Без названия')[:60]
            duration = entry.get('duration')
            dur = f" • {duration//60}:{duration%60:02d}" if duration else ""
            text += f"{i+1}. {title}{dur}\n"
            keyboard.append([InlineKeyboardButton(text=f"{i+1}. {title}", callback_data=f"play_{i}")])

        keyboard.append([InlineKeyboardButton(text="🔄 Новый поиск", callback_data="search_music")])

        await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

    except Exception as e:
        logging.error(e)
        await message.answer("Ошибка поиска. Попробуй ещё раз.")

@dp.callback_query(lambda c: c.data.startswith("play_"))
async def play_track(callback: types.CallbackQuery):
    index = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    if user_id not in user_searches or index >= len(user_searches[user_id]):
        await callback.answer("Трек не найден")
        return

    entry = user_searches[user_id][index]
    await callback.message.answer(f"⬇️ Скачиваю: {entry.get('title')}")

    try:
        video_url = f"https://youtube.com/watch?v={entry['id']}"
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(id)s.%(ext)s',
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)

        await bot.send_audio(
            chat_id=callback.message.chat.id,
            audio=types.FSInputFile(filename),
            title=info.get('title'),
            performer=info.get('uploader')
        )

        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        await callback.message.answer("Не удалось скачать трек 😔")
        logging.error(e)

    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
