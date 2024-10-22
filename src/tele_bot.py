import os
from argparse import ArgumentParser
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
    keyboard = [
        [InlineKeyboardButton("Generate Song", callback_data='generate')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Welcome to AI Cover Generator! Choose an action:', reply_markup=reply_markup)

# Button handler
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'generate':
        await query.edit_message_text(text="Please send the model name, YouTube link, and pitch (e.g., '<model_name> <link> <pitch>').")

# Generate song handler
async def generate_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Assuming the user sends model_name, YouTube link, and pitch
    song_input = update.message.text
    try:
        # Split the message into model_name, link, and pitch
        model_name, song_link, pitch_str = song_input.split()
        pitch = int(pitch_str)  # Convert pitch to integer
    except ValueError:
        # Handle error if input is not correctly formatted
        await update.message.reply_text(f"Please send a valid input in the format '<model_name> <link> <pitch>' (e.g., 'model1 https://youtube.com/abc 2').")
        return

    keep_files = False
    is_webui = False

    # Call the song_cover_pipeline function (from main.py)
    song_output = song_cover_pipeline(song_link, model_name, pitch, keep_files, is_webui)
    
    # Assuming song_cover_pipeline returns the path to the output file
    if os.path.exists(song_output):
        # Send the generated song as audio
        await update.message.reply_audio(audio=open(song_output, 'rb'))
        
        # Optionally, delete the output file after sending
        os.remove(song_output)
    else:
        await update.message.reply_text(f"An error occurred while generating the song.")

# Main function to run the bot
def main():

    application = Application.builder().token("7360013787:AAFjVrKRPa6nkune4N6JPlO14DTqqySJD_Y").build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_song))  # Generate song on text input

    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()
