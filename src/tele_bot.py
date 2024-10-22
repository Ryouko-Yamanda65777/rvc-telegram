from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import os
from main import song_cover_pipeline  # Keeping this import from your original main.py
from download_model import download_online_model  # Import your download function

# Define paths
BASE_DIR = "/content/HRVC"

output_dir = os.path.join(BASE_DIR, 'song_output')

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Define states for the conversation
GENERATE_SONG, DOWNLOAD_MODEL = range(2)

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
        return GENERATE_SONG  # Set the state for generating a song
    elif query.data == 'download_model':
        await query.edit_message_text(text="Please send the model URL and name (e.g., '<url> <model_name>').")
        return DOWNLOAD_MODEL  # Set the state for downloading a model

# Generate song handler
async def generate_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    song_input = update.message.text
    try:
        model_name, song_link, pitch_str = song_input.split()
        pitch = int(pitch_str)
    except ValueError:
        await update.message.reply_text(f"Please send a valid input in the format '<model_name> <link> <pitch>' (e.g., 'model1 https://youtube.com/abc 2').")
        return GENERATE_SONG  # Stay in the same state

    keep_files = False
    is_webui = False

    song_output = song_cover_pipeline(song_link, model_name, pitch, keep_files, is_webui)
    
    if os.path.exists(song_output):
        await update.message.reply_audio(audio=open(song_output, 'rb'))
        os.remove(song_output)
    else:
        await update.message.reply_text(f"An error occurred while generating the song.")
    
    return ConversationHandler.END  # End the conversation after song generation

# Download model handler
async def download_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    model_input = update.message.text
    try:
        url, model_name = model_input.split()
    except ValueError:
        await update.message.reply_text("Please send a valid input in the format '<url> <model_name>' (e.g., 'https://example.com/model.zip my_model').")
        return DOWNLOAD_MODEL  # Stay in the same state

    try:
        # Call the download_online_model function to download the model
        download_online_model(url, model_name)
        await update.message.reply_text(f"Model '{model_name}' downloaded successfully.")
    except Exception as e:
        await update.message.reply_text(f"Error downloading the model: {e}")
    
    return ConversationHandler.END  # End the conversation after model download

# Cancel handler to return to the main menu
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operation cancelled. Returning to the main menu.")
    return ConversationHandler.END  # End the conversation

# Main function to run the bot
def main():
    parser = ArgumentParser(description='Telegram Bot for AI Cover Generation')
    parser.add_argument('--token', type=str, help='Telegram bot token')
    args = parser.parse_args()

    application = Application.builder().token(args.token).build()

    # Conversation handler with states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GENERATE_SONG: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_song)],
            DOWNLOAD_MODEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, download_model)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Add the conversation handler to the application
    application.add_handler(conv_handler)

    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()
