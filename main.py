import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command('start'))
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Поиск музыки", callback_data="search_music")]
    ])
    await message.answer("Привет! Я Sondly Bot. Нажми кнопку для поиска музыки.", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data == 'search_music')
async def process_callback(callback: types.CallbackQuery):
    await callback.message.answer("Введите название трека или исполнителя для поиска:")
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())