import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ConversationHandler, filters, ContextTypes
)

BOT_TOKEN = '8608074874:AAFWEklW57zO8F2zewtMwsPDEKbiQ'
ADMIN_CHAT_ID = '6449930180'

logging.basicConfig(level=logging.INFO)

PROBLEM, CONTACT_WAY, PHONE = range(3)

PROBLEMS = [
    ['🔲 Укладка плитки', '🔧 Ремонт плитки'],
    ['💧 Затирка швов', '🪟 Демонтаж плитки'],
    ['📐 Консультация', '✏️ Другое']
]

CONTACT_WAYS = [
    ['📱 Позвонить мне', '💬 Написать здесь в боте']
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"👋 Привет, {name}!\n\nВы обратились в нашу компанию *Ремонт и укладка плитки*.\n\nВыберите, пожалуйста, с чем нужна помощь 👇",
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup(PROBLEMS, resize_keyboard=True)
    )
    return PROBLEM

async def get_problem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['problem'] = update.message.text
    await update.message.reply_text(
        "📞 Как вам удобнее с вами связаться?",
        reply_markup=ReplyKeyboardMarkup(CONTACT_WAYS, resize_keyboard=True)
    )
    return CONTACT_WAY

async def get_contact_way(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['contact_way'] = update.message.text
    if 'Позвонить' in update.message.text:
        await update.message.reply_text(
            "📱 Укажите ваш номер телефона:",
            reply_markup=ReplyKeyboardRemove()
        )
        return PHONE
    else:
        await finish(update, context)
        return ConversationHandler.END

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await finish(update, context)
    return ConversationHandler.END

async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = context.user_data
    phone = data.get('phone', '—')
    problem = data.get('problem', '—')
    contact = data.get('contact_way', '—')
    await update.message.reply_text(
        "✅ *Спасибо! Ваша заявка зафиксирована.*\n\nНаш менеджер свяжется с вами в ближайшее время.\n\nЕсли хотите оставить ещё одну заявку — нажмите /start",
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove()
    )
    text = (
        f"📩 *Новая заявка из бота*\n\n"
        f"👤 Имя: {user.first_name} {user.last_name or ''}\n"
        f"🆔 Username: @{user.username or 'нет'}\n"
        f"🔗 Chat ID: `{user.id}`\n\n"
        f"🔲 Проблема: {problem}\n"
        f"📞 Способ связи: {contact}\n"
        f"📱 Телефон: {phone}"
    )
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=text,
        parse_mode='Markdown'
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Диалог отменён. Напишите /start чтобы начать заново.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PROBLEM:     [MessageHandler(filters.TEXT & ~filters.COMMAND, get_problem)],
            CONTACT_WAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_contact_way)],
            PHONE:       [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    app.add_handler(conv)
    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == '__main__':
    main()
