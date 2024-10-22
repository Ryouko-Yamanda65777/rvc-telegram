import os
from argparse import ArgumentParser
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram.ext import ContextTypes
from main import song_cover_pipeline  # Keeping this import from your original main.py
from download_rvcmodels import download_online_model  # Import your download function

# Define paths
BASE_DIR = "/content/HRVC"
output_dir = os.path.join(BASE_DIR, 'song_output')

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Generate Song", callback_data='generate')],
        [InlineKeyboardButton("Download RVC Model", callback_data='download_model')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Welcome to AI Cover Generator! Choose an action:', reply_markup=reply_markup)

# Button handler
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'generate':
        await query.edit_message_text(text="Please send the model name, YouTube link, and pitch (e.g., '<model_name> <link> <pitch>').")
    elif query.data == 'download_model':
        await query.edit_message_text(text="Please send the model URL and name (e.g., '<url> <model_name>').")

# Download model handler
async def download_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    model_input = update.message.text
    try:
        # Split the message into URL and directory name
        url, model_name = model_input.split()
    except ValueError:
        # Handle error if input is not correctly formatted
        await update.message.reply_text("Please send a valid input in the format '<url> <model_name>' (e.g., 'https://example.com/model.zip my_model').")
        return

    try:
        # Call the download_online_model function to download the model
        download_online_model(url, model_name)
        await update.message.reply_text(f"Model '{model_name}' downloaded successfully.")
    except Exception as e:
        await update.message.reply_text(f"Error downloading the model: {e}")

# Generate song handler
async def generate_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    song_input = update.message.text
    try:
        model_name, song_link, pitch_str = song_input.split()
        pitch = int(pitch_str)
    except ValueError:
        await update.message.reply_text(f"Please send a valid input in the format '<model_name> <link> <pitch>' (e.g., 'model1 https://youtube.com/abc 2').")
        return

    keep_files = False
    is_webui = False

    song_output = song_cover_pipeline(song_link, model_name, pitch, keep_files, is_webui)
    
    if os.path.exists(song_output):
        await update.message.reply_audio(audio=open(song_output, 'rb'))
        os.remove(song_output)
    else:
        await update.message.reply_text(f"An error occurred while generating the song.")

# Main function to run the bot
def main():
    parser = ArgumentParser(description='Telegram Bot for AI Cover Generation')
    parser.add_argument('--token', type=str, help='Telegram bot token')
    args = parser.parse_args()

    application = Application.builder().token(args.token).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_song))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_model))  # Handle model download

    application.run_polling()

if __name__ == '__main__':
    main()
