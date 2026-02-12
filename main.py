
#TOKEN = "8175670659:AAGsZ1s0hkpt7sC_uhg0QFib8Z3nH-oHYSo"
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8175670659:AAGsZ1s0hkpt7sC_uhg0QFib8Z3nH-oHYSo"
# Mini App host qilingan manzili (masalan Vercel'dan olingan link)
APP_URL = "https://testbotms.netlify.app/" 

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    # Rasmdagi kabi majburiy a'zolik va asosiy menyu
    text = "Assalomu alaykum! Milliy sertifikat botiga xush kelibsiz."
    
    builder = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 MS testlar", web_app=WebAppInfo(url=f"{APP_URL}/tests"))],
        [
            InlineKeyboardButton(text="➕ Test yaratish", web_app=WebAppInfo(url=f"{APP_URL}/create")),
            InlineKeyboardButton(text="✅ Javob yuborish", web_app=WebAppInfo(url=f"{APP_URL}/submit"))
        ],
        [
            InlineKeyboardButton(text="👤 Mening ma'lumotlarim", web_app=WebAppInfo(url=f"{APP_URL}/profile")),
            InlineKeyboardButton(text="📊 Mening testlarim", web_app=WebAppInfo(url=f"{APP_URL}/history"))
        ],
        [InlineKeyboardButton(text="ℹ️ Yo'riqnoma", callback_data="guide")]
    ])
    
    await message.answer(text, reply_markup=builder)

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())