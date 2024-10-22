import os
from argparse import ArgumentParser
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram.ext import ContextTypes
from main import song_cover_pipeline  # Keeping this import from your original main.py

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(BASE_DIR, 'song_output')

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Welcome to AI Cover Generator! Please send the YouTube link to generate a song.')

# Generate song handler
async def generate_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text

    # Check if the user is providing a YouTube link
    if user_input.startswith("http") or user_input.startswith("www"):
        context.user_data['song_input'] = user_input
        await update.message.reply_text('Please provide the model name you want to use.')
    else:
        # Handle invalid link
        await update.message.reply_text('Please provide a valid YouTube link.')

# Get model name handler
async def get_model_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    model_name = update.message.text
    context.user_data['model_name'] = model_name
    await update.message.reply_text('Please provide the pitch value (e.g., -3, 0, 3).')

# Get pitch handler
async def get_pitch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        pitch = float(update.message.text)
        context.user_data['pitch'] = pitch

        # Start the song generation process
        song_input = context.user_data.get('song_input')
        model_name = context.user_data.get('model_name', 'default_model')  # Default model if not provided
        keep_files = False
        is_webui = False

        # Call the song_cover_pipeline function (from main.py)
        song_output = song_cover_pipeline(song_input, model_name, pitch, keep_files, is_webui)

        # Assuming song_cover_pipeline returns the path to the output file
        if os.path.exists(song_output):
            # Send the generated song as audio
            await update.message.reply_audio(audio=open(song_output, 'rb'))
            
            # Optionally, delete the output file after sending
            os.remove(song_output)
        else:
            await update.message.reply_text(f"An error occurred while generating the song.")

    except ValueError:
        await update.message.reply_text('Please provide a valid numeric pitch value.')

# Main function to run the bot
def main():
    parser = ArgumentParser(description='Telegram Bot for AI Cover Generation')
    parser.add_argument('--token', type=str, help='Telegram bot token')
    args = parser.parse_args()

    application = Application.builder().token(args.token).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_model_name))  # Get model name
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_pitch))  # Get pitch
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_song))  # Generate song on text input

    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()
