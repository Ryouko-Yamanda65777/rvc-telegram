import json
import os
import shutil
import urllib.request
import zipfile
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Your existing imports and functions here (get_current_models, download_online_model, etc.)

# Constants
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
mdxnet_models_dir = os.path.join(BASE_DIR, 'mdxnet_models')
rvc_models_dir = os.path.join(BASE_DIR, 'rvc_models')
output_dir = os.path.join(BASE_DIR, 'song_output')

# Telegram Bot Configuration
TOKEN = '7360013787:AAFjVrKRPa6nkune4N6JPlO14DTqqySJD_Y'

def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Generate", callback_data='generate'),
            InlineKeyboardButton("Download", callback_data='download'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Welcome! Please choose an option:', reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == 'generate':
        query.edit_message_text(text="Please send your song input (comma-separated):")
        return  # Wait for song input

    elif query.data == 'download':
        query.edit_message_text(text="Please send the download link and model name (comma-separated):")
        return  # Wait for download input

def handle_message(update: Update, context: CallbackContext) -> None:
    user_input = update.message.text

    if ',' in user_input:
        parts = [part.strip() for part in user_input.split(',')]
        
        if len(parts) == 2:  # Handle both generate and download
            if update.message.reply_to_message.text.startswith("Please send your song input"):
                song_input = parts[0]
                # Call your song_cover_pipeline function here with song_input
                # Example: result = song_cover_pipeline(song_input, ...)
                update.message.reply_text(f"Song generated for input: {song_input}")
            elif update.message.reply_to_message.text.startswith("Please send the download link"):
                model_zip_link = parts[0]
                model_name = parts[1]
                try:
                    message = download_online_model(model_zip_link, model_name)
                    update.message.reply_text(message)
                except Exception as e:
                    update.message.reply_text(f"Error: {str(e)}")
        else:
            update.message.reply_text("Please provide exactly two inputs separated by a comma.")
    else:
        update.message.reply_text("Invalid input format. Please provide inputs separated by a comma.")

def main() -> None:
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
