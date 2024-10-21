import json
import os
import shutil
import urllib.request
import zipfile
from argparse import ArgumentParser
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram.ext import ContextTypes
from main import song_cover_pipeline  # Keep this import from your original main.py

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
mdxnet_models_dir = os.path.join(BASE_DIR, 'mdxnet_models')
rvc_models_dir = os.path.join(BASE_DIR, 'rvc_models')
output_dir = os.path.join(BASE_DIR, 'song_output')

# Function to get current models
def get_current_models(models_dir):
    models_list = os.listdir(models_dir)
    items_to_remove = ['hubert_base.pt', 'MODELS.txt', 'public_models.json', 'rmvpe.pt']
    return [item for item in models_list if item not in items_to_remove]

# Update models list handler
async def update_models_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    models = get_current_models(rvc_models_dir)
    keyboard = [[InlineKeyboardButton(model, callback_data=model)] for model in models]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Choose a voice model:', reply_markup=reply_markup)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Generate Song", callback_data='generate')],
        [InlineKeyboardButton("Upload Model", callback_data='upload')],
        [InlineKeyboardButton("Download Model", callback_data='download')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Welcome to AI Cover Generator! Choose an action:', reply_markup=reply_markup)

# Button handler
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'generate':
        await query.edit_message_text(text="Please send the YouTube link or upload the file to generate a song.")

    elif query.data == 'upload':
        await query.edit_message_text(text="Please upload a zip file containing the model.")

    elif query.data == 'download':
        await query.edit_message_text(text="Please provide the download link for the model.")

# File upload handler
async def upload_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    if file.mime_type == 'application/zip':
        file_name = file.file_name
        await file.download_to_drive(f"{rvc_models_dir}/{file_name}")
        await update.message.reply_text(f"Model {file_name} uploaded successfully!")
    else:
        await update.message.reply_text("Please upload a valid zip file.")

# Download model handler
async def download_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.split(" ")
    if len(message) == 2:
        url = message[1]
        dir_name = os.path.basename(url)
        try:
            download_online_model(url, dir_name)
            await update.message.reply_text(f"Model {dir_name} downloaded successfully!")
        except Exception as e:
            await update.message.reply_text(f"Error: {str(e)}")
    else:
        await update.message.reply_text("Please provide the download link in the format: /download <url>")

# Generate song handler
async def generate_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Assuming the user sends a YouTube link
    song_input = update.message.text
    model_name = "default_model"  # You can prompt the user to select a model
    pitch = 0
    keep_files = False
    is_webui = False

    # Call the song_cover_pipeline function (from main.py)
    song_output = song_cover_pipeline(song_input, model_name, pitch, keep_files, is_webui)
    await update.message.reply_text(f"Song generated: {song_output}")

# Main function to run the bot
def main():
    parser = ArgumentParser(description='Telegram Bot for AI Cover Generation')
    parser.add_argument('--token', type=str, help='Telegram bot token')
    args = parser.parse_args()

    application = Application.builder().token(args.token).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_song))  # Generate song on text input
    application.add_handler(MessageHandler(filters.Document.ZIP, upload_model))  # Handle model file upload
    application.add_handler(CommandHandler("download", download_model))  # Handle model download

    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()
