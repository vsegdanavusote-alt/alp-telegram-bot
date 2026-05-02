import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, ConversationHandler, Filters

TOKEN = os.environ.get('TELEGRAM_TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID', '8520327537'))

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
NAME, PHONE, SERVICE = range(3)

def main_menu_keyboard():
    return ReplyKeyboardMarkup([
        ["📝 Оставить заявку"],
        ["❓ FAQ"],
        ["📞 Контакты"],
        ["ℹ️ О нас"]
    ], resize_keyboard=True)

def services_keyboard():
    return ReplyKeyboardMarkup([
        ["1. Мойка фасадов", "2. Утепление"],
        ["3. Ремонт кровли", "4. Гидроизоляция"],
        ["5. Монтаж рекламы", "6. Молниезащита"],
        ["7. Другое", "🔙 Назад"]
    ], resize_keyboard=True)


def start(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Привет! 🧗\n\nЯ бот компании «Альп-Пром» — промышленный альпинизм в Харькове.\n\nЧем могу помочь?",
        reply_markup=main_menu_keyboard()
    )

def order_request(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("📝 Оставьте заявку\n\nКак вас зовут?", reply_markup=ReplyKeyboardMarkup([["Отмена"]], resize_keyboard=True))
    return NAME

def get_name(update: Update, context: CallbackContext) -> int:
    context.user_data['name'] = update.message.text
    update.message.reply_text("📱 Введите номер телефона:", reply_markup=ReplyKeyboardMarkup([["Отмена"]], resize_keyboard=True))
    return PHONE

def get_phone(update: Update, context: CallbackContext) -> int:
    context.user_data['phone'] = update.message.text
    update.message.reply_text("🔧 Выберите услугу:", reply_markup=services_keyboard())
    return SERVICE

def get_service(update: Update, context: CallbackContext) -> int:
    service = update.message.text
    if service == "🔙 Назад":
        start(update, context)
        return ConversationHandler.END
    if ". " in service:
        service = service.split(". ")[1]
    
    context.user_data['service'] = service
    
    msg = f"📥 Новая заявка!\n\nИмя: {context.user_data['name']}\nТелефон: {context.user_data['phone']}\nУслуга: {service}"
    context.bot.send_message(chat_id=ADMIN_ID, text=msg)
    
    update.message.reply_text(
        f"✅ Спасибо, {context.user_data['name']}!\n\nЗаявка принята!\nМы свяжемся с вами! 📞",
        reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Отменено", reply_markup=main_menu_keyboard())
    return ConversationHandler.END

def faq(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("❓ Частые вопросы\n\n💰 Стоимость:\n• Мойка фасадов: от 40 грн/м²\n• Утепление: от 750 грн/м²\n\n⏱️ Сроки: 1-7 дней\n📋 Договор: Да\n💳 Оплата: Наличный/безналичный", reply_markup=main_menu_keyboard())

def contacts(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("📞 Контакты\n\n📍 г. Харьков\n📱 +38 (073) 175-17-57\n📱 +38 (067) 570-49-87\n✉️ alppromukr@gmail.com\n\n⏰ Пн-Сб 9:00-18:00", reply_markup=main_menu_keyboard())

def about(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("ℹ️ О нас\n\n🧗 Работаем с 2013 года\n✅ 500+ объектов\n\nУслуги:\n• Мойка/утепление фасадов\n• Ремонт кровли\n• Гидроизоляция\n• Монтаж рекламы\n\nГарантия до 36 месяцев!", reply_markup=main_menu_keyboard())

def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    if text == "📝 Оставить заявку":
        order_request(update, context)
    elif text == "❓ FAQ":
        faq(update, context)
    elif text == "📞 Контакты":
        contacts(update, context)
    elif text == "ℹ️ О нас":
        about(update, context)
    else:
        start(update, context)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    conv = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("📝 Оставить заявку"), order_request)],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
            PHONE: [MessageHandler(Filters.text & ~Filters.command, get_phone)],
            SERVICE: [MessageHandler(Filters.text & ~Filters.command, get_service)],
        },
        fallbacks=[MessageHandler(Filters.regex("Отмена"), cancel)]
    )
    
    dp.add_handler(conv)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    logger.info("Бот запущен!")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()