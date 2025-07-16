
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

BOT_TOKEN = '7990044460:AAFMYiXyWzeGDZoiEK1iIQi6cDA61hFcEPc'
ADMIN_ID = 2077750894

def get_start_keyboard():
    keyboard = [[InlineKeyboardButton("▶️ Старт", callback_data="start_chat")]]
    return InlineKeyboardMarkup(keyboard)

def get_main_keyboard():
    keyboard = [[InlineKeyboardButton("✉️ Отправить сообщение x771", callback_data="send_anon")]]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Добро пожаловать в анонимный чат.",
        reply_markup=get_start_keyboard()
    )

async def handle_start_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "Ты можешь отправить анонимное сообщение x771:",
        reply_markup=get_main_keyboard()
    )

async def handle_send_anon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("✏️ Напиши сообщение, и я анонимно передам его x771.")
    context.user_data["awaiting_message"] = True

async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_message"):
        context.user_data["awaiting_message"] = False
        user = update.message.from_user
        username = user.username or f"{user.first_name} {user.last_name or ''}"

        sent = await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📩 Новое анонимное сообщение:\n\n{update.message.text}\n\n👤 От: @{username if user.username else 'без username'}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Ответить", callback_data=f"reply_{user.id}")]
            ])
        )

        context.bot_data[sent.message_id] = user.id
        await update.message.reply_text("✅ Сообщение отправлено x771!")
    else:
        await update.message.reply_text("Нажми кнопку, чтобы отправить сообщение.")

async def admin_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID:
        return
    target_user_id = int(query.data.split("_")[1])
    context.user_data["reply_to_user"] = target_user_id
    await query.message.reply_text("✍️ Введите сообщение для ответа пользователю.")

async def admin_send_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == ADMIN_ID and context.user_data.get("reply_to_user"):
        user_id = context.user_data.pop("reply_to_user")
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📬 Ответ от x771:\n\n{update.message.text}"
            )
            await update.message.reply_text("✅ Ответ отправлен.")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")
    elif update.message.from_user.id == ADMIN_ID:
        await update.message.reply_text("❗️Сначала нажми кнопку 'Ответить' на сообщении.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_start_chat, pattern="^start_chat$"))
    app.add_handler(CallbackQueryHandler(handle_send_anon, pattern="^send_anon$"))
    app.add_handler(CallbackQueryHandler(admin_reply_handler, pattern="^reply_\\d+$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_message))
    app.add_handler(MessageHandler(filters.TEXT & filters.User(ADMIN_ID), admin_send_response))

    print("🤖 Бот запущен...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
