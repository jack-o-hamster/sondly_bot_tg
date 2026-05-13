import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import openai

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv('BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command('start'))
async def start(message: types.Message):
    await message.answer(
        "🎵 Привет! Я бот музыкальных фактов.\n\n"
        "Напиши название трека или имя артиста — и я расскажу интересный факт про него."
    )

@dp.message()
async def get_music_fact(message: types.Message):
    query = message.text.strip()
    if len(query) < 2:
        await message.answer("❌ Напиши хотя бы 2 символа.")
        return

    await message.answer(f"🔍 Ищу интересный факт про «{query}»...")

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Ты — эксперт по музыке. Отвечай только на русском языке. Давай один интересный, малоизвестный факт про артиста или трек. Максимум 3-4 предложения. Будь увлекательным."
                },
                {
                    "role": "user",
                    "content": f"Расскажи интересный факт про: {query}"
                }
            ],
            max_tokens=350,
            temperature=0.85
        )
        
        fact = response.choices[0].message.content.strip()
        await message.answer(f"🎸 **Факт про {query}:**\n\n{fact}\n\nНапиши другого артиста для нового факта.")

    except openai.RateLimitError:
        await message.answer("❌ Превышен лимит запросов OpenAI. Подожди немного.")
    except openai.AuthenticationError:
        await message.answer("❌ Ошибка ключа OpenAI. Проверь OPENAI_API_KEY.")
    except Exception as e:
        error_msg = f"❌ Ошибка: {type(e).__name__}: {str(e)}"
        logging.error(error_msg)
        await message.answer(error_msg)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
