import sqlite3
from datetime import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    CallbackContext,
)

# ---------------- TOKEN ----------------
TOKEN = "shu"

# ---------------- KANALLAR ----------------
CHANNELS = ["@kk2123", "@powwer3113"]

# ---------------- DATABASE ----------------
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

# Jadval yaratish
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    invited_by INTEGER,
    invites INTEGER DEFAULT 0
)
""")
conn.commit()

# Agar ustunlar yo‘q bo‘lsa, qo‘shamiz
try:
    cursor.execute("ALTER TABLE users ADD COLUMN subscribed_channels INTEGER DEFAULT 0")
except:
    pass

try:
    cursor.execute("ALTER TABLE users ADD COLUMN score INTEGER DEFAULT 0")
except:
    pass

conn.commit()

# ---------------- OBUNA TEKSHIRISH ----------------
async def check_subscription(user_id, bot):
    count = 0
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in ["left", "kicked"]:
                count += 1
        except:
            pass
    return count

# ---------------- OBUNA XABARI ----------------
async def send_subscription_message(update_or_query, context):
    buttons = [[InlineKeyboardButton(f"📢 {c}", url=f"https://t.me/{c[1:]}")] for c in CHANNELS]
    buttons.append([InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")])
    markup = InlineKeyboardMarkup(buttons)
    text = "❗️ Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:"

    if hasattr(update_or_query, "message") and update_or_query.message:
        await update_or_query.message.reply_text(text, reply_markup=markup)
    else:
        await update_or_query.edit_message_text(text, reply_markup=markup)

# ---------------- PANEL YUBORISH ----------------
async def send_panel(update_or_query, context, user_id=None):
    if not user_id:
        user_id = update_or_query.effective_user.id

    cursor.execute("SELECT invites, score FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    invites = result[0] if result else 0
    score = result[1] if result else 0

    bot_username = (await context.bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start={user_id}"

    text = f"""👤 Sizning hisobingiz

👥 Takliflar: {invites}
🥇 Reyting ball: {score}

🔗 Referal link:"""

    buttons = [
        [InlineKeyboardButton("📋 Nusxa olish", switch_inline_query=ref_link)],
        [
            InlineKeyboardButton("🔄 Yangilash", callback_data="refresh"),
            InlineKeyboardButton("🏆 TOP 10", callback_data="top")
        ]
    ]
    markup = InlineKeyboardMarkup(buttons)

    if hasattr(update_or_query, "message") and update_or_query.message:
        await update_or_query.message.reply_text(text, reply_markup=markup)
    else:
        await update_or_query.edit_message_text(text, reply_markup=markup)

# ---------------- /START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args

    subscribed_count = await check_subscription(user.id, context.bot)
    if subscribed_count < len(CHANNELS):
        await send_subscription_message(update, context)
        return

    inviter_id = None
    if args:
        try:
            inviter_id = int(args[0])
        except:
            inviter_id = None

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user.id,))
    existing_user = cursor.fetchone()

    if not existing_user:
        cursor.execute(
            "INSERT INTO users (user_id, invited_by, invites, subscribed_channels, score) VALUES (?, ?, 0, ?, ?)",
            (user.id, inviter_id, subscribed_count, subscribed_count)
        )
        conn.commit()


        # Inviter score update
        if inviter_id and inviter_id != user.id:
            cursor.execute("SELECT subscribed_channels FROM users WHERE user_id=?", (user.id,))
            tmp = cursor.fetchone()
            child_sub = tmp[0] if tmp else 0
            cursor.execute(
                "UPDATE users SET invites = invites + 1, score = score + ? WHERE user_id=?",
                (child_sub, inviter_id)
            )
            conn.commit()
    else:
        cursor.execute(
            "UPDATE users SET subscribed_channels=?, score=? WHERE user_id=?",
            (subscribed_count, subscribed_count, user.id)
        )
        conn.commit()

    await send_panel(update, context)

# ---------------- TEKSHIRISH BUTTON ----------------
async def check_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    subscribed_count = await check_subscription(query.from_user.id, context.bot)
    if subscribed_count < len(CHANNELS):
        await send_subscription_message(query, context)
        return

    cursor.execute(
        "UPDATE users SET subscribed_channels=?, score=? WHERE user_id=?",
        (subscribed_count, subscribed_count, query.from_user.id)
    )
    conn.commit()

    cursor.execute("SELECT invited_by FROM users WHERE user_id=?", (query.from_user.id,))
    tmp = cursor.fetchone()
    inviter_id = tmp[0] if tmp else None
    if inviter_id:
        cursor.execute(
            "UPDATE users SET score = score + ? WHERE user_id=?",
            (subscribed_count, inviter_id)
        )
        conn.commit()

    await send_panel(query, context, query.from_user.id)

# ---------------- TOP 10 ----------------
async def top(update, context):
    chat_id = update.message.chat_id if hasattr(update, "message") and update.message else update.callback_query.from_user.id

    cursor.execute("""
        SELECT user_id, score FROM users
        WHERE score>0
        ORDER BY score DESC
        LIMIT 10
    """)
    top_users = cursor.fetchall()

    if not top_users:
        await context.bot.send_message(chat_id=chat_id, text="Hali TOP 10 uchun foydalanuvchilar yo‘q.")
        return

    text = "🏆 TOP 10 referallar:\n\n"
    for i, (user_id, score) in enumerate(top_users, start=1):
        try:
            user = await context.bot.get_chat(user_id)
            username = f"@{user.username}" if user.username else user.first_name
        except:
            username = str(user_id)
        text += f"{i}. {username} — {score} ball\n"

    await context.bot.send_message(chat_id=chat_id, text=text)

# ---------------- OYLIGI RESET ----------------
async def monthly_reset(context: CallbackContext):
    cursor.execute("UPDATE users SET invites=0, score=0")
    conn.commit()
    print("Oylik referal reset amalga oshirildi.")

# ---------------- APP ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(check_button, pattern="check_sub|refresh"))
app.add_handler(CallbackQueryHandler(top, pattern="top"))

job_queue = app.job_queue
job_queue.run_daily(monthly_reset, time=time(hour=0, minute=0), days=(1,))

print("Bot ishga tushdi...")
app.run_polling()

