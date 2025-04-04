from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import os

class AdminPanel:
    def __init__(self, database):
        self.db = database

    async def show_admin_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("📊 Статистика", callback_data='admin_stats')],
            [InlineKeyboardButton("📥 Экспорт базы данных", callback_data='admin_export')],
            [InlineKeyboardButton("👥 Список пользователей", callback_data='admin_users')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Админ-панель\nВыберите действие:",
            reply_markup=reply_markup
        )

    async def handle_admin_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if query.data == 'admin_stats':
            await self.show_stats(update, context)
        elif query.data == 'admin_export':
            await self.export_database(update, context)
        elif query.data == 'admin_users':
            await self.show_users_list(update, context)

    async def show_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        stats = self.db.get_user_stats()
        message = (
            f"📊 Статистика бота:\n\n"
            f"👥 Всего пользователей: {stats['total_users']}\n"
            f"✅ Активных пользователей: {stats['active_users']}"
        )
        await update.callback_query.edit_message_text(message)

    async def export_database(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        filename = self.db.export_users_to_csv()
        with open(filename, 'rb') as file:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=file,
                filename=filename
            )
        os.remove(filename)
        await update.callback_query.edit_message_text("✅ База данных успешно экспортирована")

    async def show_users_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        users = self.db.get_all_users()
        message = "👥 Список пользователей:\n\n"
        
        for user in users[:10]:  # Показываем только первые 10 пользователей
            message += (
                f"ID: {user.user_id}\n"
                f"Имя: {user.first_name}\n"
                f"Username: @{user.username}\n"
                f"Язык: {user.language_code}\n"
                f"Статус: {'Активен' if user.is_active else 'Неактивен'}\n"
                f"Последняя активность: {user.last_activity}\n\n"
            )
        
        if len(users) > 10:
            message += f"... и еще {len(users) - 10} пользователей"
            
        await update.callback_query.edit_message_text(message) 
