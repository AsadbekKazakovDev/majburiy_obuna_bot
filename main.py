
#TOKEN = "8175670659:AAGsZ1s0hkpt7sC_uhg0QFib8Z3nH-oHYSo"
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

# 1. SOZLAMALAR
TOKEN = "8175670659:AAGsZ1s0hkpt7sC_uhg0QFib8Z3nH-oHYSo" # BotFather dan olingan token
WEB_APP_URL = "https://sizning-saytingiz.vercel.app" # Mini App manzili

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 2. START KOMANDASI
@dp.message(Command("start"))
async def start_command(message: types.Message):
    # Rasmdagi kabi chiroyli menyu tuzilmasi
    builder = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 MS testlar", web_app=WebAppInfo(url=WEB_APP_URL))],
        [
            InlineKeyboardButton(text="➕ Test yaratish", web_app=WebAppInfo(url=f"{WEB_APP_URL}/create")),
            InlineKeyboardButton(text="✅ Javob yuborish", web_app=WebAppInfo(url=f"{WEB_APP_URL}/submit"))
        ],
        [
            InlineKeyboardButton(text="👤 Mening ma'lumotlarim", callback_data="my_info"),
            InlineKeyboardButton(text="📊 Mening testlarim", callback_data="my_tests")
        ],
        [InlineKeyboardButton(text="ℹ️ Yo'riqnoma", callback_data="guide")]
    ])

    await message.answer(
        f"Assalomu alaykum, {message.from_user.full_name}!\n"
        "Milliy sertifikat botiga xush kelibsiz. Botdan foydalanish uchun quyidagi menyuni tanlang:",
        reply_markup=builder
    )

# 3. YO'RIQNOMA UCHUN CALLBACK
@dp.callback_query(F.data == "guide")
async def guide_handler(callback: types.CallbackQuery):
    await callback.message.answer(
        "📖 **Botdan foydalanish yo'riqnomasi:**\n\n"
        "1. 'MS testlar' bo'limiga kiring.\n"
        "2. Fanni tanlang va savollarga javob bering.\n"
        "3. Natijalaringiz avtomatik saqlanadi."
    )
    await callback.answer()

async def main():
    logging.basicConfig(level=logging.INFO)
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi")