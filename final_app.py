import logging
import ollama
import nest_asyncio
import os

from telegram import ForceReply, Update
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ApplicationBuilder

from telegram import ReplyKeyboardMarkup, KeyboardButton
# Define the keyboard layout with buttons
keyboard = [
    [KeyboardButton("Кнопка 1"), KeyboardButton("Кнопка 2")],
    [KeyboardButton("Кнопка 3"), KeyboardButton("Кнопка 4")],
]

# Create a ReplyKeyboardMarkup object with the defined keyboard layout
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

nest_asyncio.apply()

# Включаем ведение журнала
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
load_dotenv('config.env') 
# Токен, который вы получили от @BotFather
TOKEN = os.getenv('TOKEN') # Replace with your actual token

# Словарь для хранения данных пользователей
user_ids = {}
context_memory = {}

# Функция для обработки команды /start
async def start(update: Update, context) -> None:
    await update.message.reply_text('Привет! Я чат-бот. Чем могу помочь?',
                                    reply_markup=ForceReply(selective=True))

# Функция для обработки обычных сообщений
async def handle_message(update: Update, context):
    user_id = update.effective_user.id
    if user_id not in user_ids:
        user_ids[user_id] = {'last_message': None, 'preferences': {}}
        context_memory[user_id] = []

    message_text = update.message.text
    context_messages = context_memory[user_id]

    # Добавляем новое сообщение в контекст
    context_messages.append({'role': 'user', 'content': message_text})

    # Ограничиваем историю контекста последними 8 сообщениями
    context_memory[user_id] = context_messages[-8:]

    try:
        # Call the ollama.chat function with the context messages
        # local model 
        response = ollama.chat(model='mistral-nemo:12b-instruct-2407-q3_K_L', messages=context_memory[user_id])
        # Отправляем ответ пользователю
        await update.message.reply_text(response['message']['content'])
    except Exception as e:
        logging.error(f"Error while getting response from ollama: {e}")
        await update.message.reply_text('Произошла ошибка, попробуйте позже.')

# Основная функция
async def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
