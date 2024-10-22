import json
import os
import shutil
import urllib.request
import zipfile
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from main import song_cover_pipeline  # Import the pipeline

# Constants
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
mdxnet_models_dir = os.path.join(BASE_DIR, 'mdxnet_models')
rvc_models_dir = os.path.join(BASE_DIR, 'rvc_models')
output_dir = os.path.join(BASE_DIR, 'song_output')

# Telegram Bot Configuration
TOKEN = '7360013787:AAFjVrKRPa6nkune4N6JPlO14DTqqySJD_Y'

def extract_zip(extraction_folder, zip_name):
    os.makedirs(extraction_folder)
    with zipfile.ZipFile(zip_name, 'r') as zip_ref:
        zip_ref.extractall(extraction_folder)
    os.remove(zip_name)

    index_filepath, model_filepath = None, None
    for root, dirs, files in os.walk(extraction_folder):
        for name in files:
            if name.endswith('.index') and os.stat(os.path.join(root, name)).st_size > 1024 * 100:
                index_filepath = os.path.join(root, name)

            if name.endswith('.pth') and os.stat(os.path.join(root, name)).st_size > 1024 * 1024 * 40:
                model_filepath = os.path.join(root, name)

    if not model_filepath:
        raise Exception(f'No .pth model file was found in the extracted zip. Please check {extraction_folder}.')

    # move model and index file to extraction folder
    os.rename(model_filepath, os.path.join(extraction_folder, os.path.basename(model_filepath)))
    if index_filepath:
        os.rename(index_filepath, os.path.join(extraction_folder, os.path.basename(index_filepath)))

    # remove any unnecessary nested folders
    for filepath in os.listdir(extraction_folder):
        if os.path.isdir(os.path.join(extraction_folder, filepath)):
            shutil.rmtree(os.path.join(extraction_folder, filepath))


def download_online_model(url, dir_name):
    try:
        zip_name = url.split('/')[-1]
        extraction_folder = os.path.join(rvc_models_dir, dir_name)
        if os.path.exists(extraction_folder):
            raise Exception(f'Voice model directory {dir_name} already exists! Choose a different name for your voice model.')

        if 'pixeldrain.com' in url:
            url = f'https://pixeldrain.com/api/file/{zip_name}'

        urllib.request.urlretrieve(url, zip_name)
        extract_zip(extraction_folder, zip_name)
        return f'[+] {dir_name} Model successfully downloaded!'

    except Exception as e:
        raise Exception(str(e))


async def start(update: Update, context) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Generate", callback_data='generate'),
            InlineKeyboardButton("Download", callback_data='download'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Welcome! Please choose an option:', reply_markup=reply_markup)


async def button(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'generate':
        await query.edit_message_text(text="Please send your song input (comma-separated):")
        return  # Wait for song input

    elif query.data == 'download':
        await query.edit_message_text(text="Please send the download link and model name (comma-separated):")
        return  # Wait for download input


async def handle_message(update: Update, context) -> None:
    user_input = update.message.text

    if ',' in user_input:
        parts = [part.strip() for part in user_input.split(',')]

        if len(parts) == 2:
            if update.message.reply_to_message and update.message.reply_to_message.text.startswith("Please send your song input"):
                song_input = parts[0]
                model_input = parts[1]
                try:
                    result = song_cover_pipeline(song_input, model_input)  # Call your pipeline
                    await update.message.reply_text(f"Song generated successfully: {result}")
                except Exception as e:
                    await update.message.reply_text(f"Error generating song: {str(e)}")
            elif update.message.reply_to_message and update.message.reply_to_message.text.startswith("Please send the download link"):
                model_zip_link = parts[0]
                model_name = parts[1]
                try:
                    message = download_online_model(model_zip_link, model_name)
                    await update.message.reply_text(message)
                except Exception as e:
                    await update.message.reply_text(f"Error: {str(e)}")
        else:
            await update.message.reply_text("Please provide exactly two inputs separated by a comma.")
    else:
        await update.message.reply_text("Invalid input format. Please provide inputs separated by a comma.")


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
