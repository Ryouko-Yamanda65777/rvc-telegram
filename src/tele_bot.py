import os
from argparse import ArgumentParser
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram.ext import ContextTypes
from main import song_cover_pipeline  # Keeping this import from your original main.py
from webui import download_online_model  # Import the download function

TELEGRAM_BOT_TOKEN="7360013787:AAFjVrKRPa6nkune4N6JPlO14DTqqySJD_Y"


# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(BASE_DIR, 'song_output')

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Generate Song", callback_data='generate')],
        [InlineKeyboardButton("Download Model", callback_data='download_model')],
        [InlineKeyboardButton("Help", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Welcome to AICoverGen! Choose an option below:', reply_markup=reply_markup)

# Button handler
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'generate':
        await query.edit_message_text(text="Please send the model name, YouTube link, and pitch (e.g., '<model_name> <link> <pitch>')\nNote: pitch 1 for female and pitch -1 for male.")
    
    elif query.data == 'download_model':
        await query.edit_message_text(text="Please send the model name and URL in the format '<model_name> <url>'.")

    elif query.data == 'help':
        help_text = (
            "To generate a song, follow these steps:\n"
            "1. Click 'Generate Song'.\n"
            "2. Send a message in the format '<model_name> <link> <pitch>' (e.g., 'model1 https://youtube.com/abc 2').\n"
            "3. Wait for the bot to process and return the generated song.\n"
            "Pitch: Use 1 for female voice, -1 for male voice.\n\n"
            "To download a model:\n"
            "1. Click 'Download Model'.\n"
            "2. Send a message in the format '<model_name> <url>' to specify the model name and the download URL."
        )
        await query.edit_message_text(text=help_text)

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

# Download model handler with custom name
async def download_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    model_input = update.message.text
    try:
        # Split the input into model name and URL
        model_name, model_url = model_input.split()
    except ValueError:
        await update.message.reply_text(f"Please send a valid input in the format '<model_name> <url>' (e.g., 'model1 https://model.com/abc').")
        return

    if not model_url.startswith("http"):
        await update.message.reply_text("Please send a valid URL.")
        return

    try:
        # Call the function to download the model with a custom name
        download_online_model(model_url, model_name)
        await update.message.reply_text(f"Model '{model_name}' downloaded successfully from {model_url}!")
    except Exception as e:
        await update.message.reply_text(f"Failed to download the model. Error: {str(e)}")

# Main function to run the bot
def main():
    bot_token = TELEGRAM_BOT_TOKEN

    if not bot_token:
        raise ValueError("Bot token not found. Set the TELEGRAM_BOT_TOKEN environment variable.")

    application = Application.builder().token(bot_token).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_song))  # Generate song on text input
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_model))  # Download model on text input

    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()

