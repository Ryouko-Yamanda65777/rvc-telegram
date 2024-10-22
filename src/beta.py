import os
import json
import urllib.request
import zipfile
import telebot
from telebot import types

# Retrieve the API token from environment variable

API_TOKEN='7360013787:AAFjVrKRPa6nkune4N6JPlO14DTqqySJD_Y'



# Initialize the bot
bot = telebot.TeleBot(API_TOKEN)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
rvc_models_dir = os.path.join(BASE_DIR, 'rvc_models')

def get_current_models(models_dir):
    models_list = os.listdir(models_dir)
    items_to_remove = ['hubert_base.pt', 'MODELS.txt', 'public_models.json', 'rmvpe.pt']
    return [item for item in models_list if item not in items_to_remove]

voice_models = get_current_models(rvc_models_dir)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = "Welcome to the AI Cover Generator Bot! You can:\n" \
                   "- Use /generate to generate a cover song.\n" \
                   "- Use /download to download a model."
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['generate'])
def generate_cover(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for model in voice_models:
        markup.add(types.KeyboardButton(model))
    bot.reply_to(message, "Please choose a voice model:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in voice_models)
def handle_model_selection(message):
    selected_model = message.text
    bot.send_message(message.chat.id, f"You selected: {selected_model}\nSend me a song input (YouTube link or local file path).")
    
    # Store the selected model for later use (in a global or user-specific context)
    bot.user_data[message.from_user.id] = {'model': selected_model}

@bot.message_handler(content_types=['text'])
def handle_song_input(message):
    # Retrieve the selected model from user_data
    user_data = bot.user_data.get(message.from_user.id)
    if not user_data or 'model' not in user_data:
        bot.send_message(message.chat.id, "Please select a model first using /generate.")
        return

    selected_model = user_data['model']
    song_input = message.text
    bot.send_message(message.chat.id, f"You sent: {song_input}\nGenerating cover...")

    # Here you would call your song_cover_pipeline function with the selected model and song input
    try:
        # Call your AI cover generation function
        ai_cover_path = song_cover_pipeline(song_input, selected_model)  # Modify this line to match your function's signature
        # Send the generated AI cover back to the user
        with open(ai_cover_path, 'rb') as audio_file:
            bot.send_audio(message.chat.id, audio_file)
    except Exception as e:
        bot.send_message(message.chat.id, f"Error during generation: {str(e)}")

@bot.message_handler(commands=['download'])
def download_model(message):
    bot.send_message(message.chat.id, "Send me the download link for the model:")

@bot.message_handler(content_types=['text'])
def handle_download_link(message):
    url = message.text
    dir_name = url.split('/')[-1].replace('.zip', '')  # Simple way to create a name from URL
    # Implement downloading and extracting logic here
    # download_online_model(url, dir_name)

    bot.reply_to(message, f"Model downloaded and extracted to: {dir_name}.")

# To handle errors
@bot.error_handler
def handle_errors(error):
    bot.send_message(error.chat.id, "An error occurred. Please try again.")

if __name__ == '__main__':
    bot.polling()
