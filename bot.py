import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv
from database import Database
from admin_panel import AdminPanel

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружениядай
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
ADMIN_IDS = [int(id) for id in os.getenv('ADMIN_IDS', '').split(',') if id]

class Bot:
    def __init__(self):
        self.db = Database()
        self.admin_panel = AdminPanel(self.db)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        user_data = {
            'user_id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'language_code': user.language_code
        }
        
        # Сохраняем или обновляем данные пользователя
        self.db.add_or_update_user(user_data)
        
        keyboard = [
            [InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru'),
             InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Выберите язык / Choose language",
            reply_markup=reply_markup
        )

    async def handle_language_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        language = query.data.split('_')[1]
        user_id = query.from_user.id
        
        # Обновляем язык пользователя в базе данных
        self.db.update_user_language(user_id, language)
        
        if language == 'ru':
            await query.edit_message_text("Язык установлен на русский")
        else:
            await query.edit_message_text("Language set to English")

    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in ADMIN_IDS:
            await update.message.reply_text("У вас нет доступа к этой команде")
            return
            
        await self.admin_panel.show_admin_menu(update, context)

    async def handle_admin_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in ADMIN_IDS:
            await update.callback_query.answer("У вас нет доступа к этой команде")
            return
            
        await self.admin_panel.handle_admin_callback(update, context)

def main():
    bot = Bot()
    application = Application.builder().token(TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("admin", bot.admin_command))
    application.add_handler(CallbackQueryHandler(bot.handle_language_selection, pattern='^lang_'))
    application.add_handler(CallbackQueryHandler(bot.handle_admin_callback, pattern='^admin_'))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main() 
