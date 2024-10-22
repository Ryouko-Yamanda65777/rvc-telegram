# RVC-Telegram Bot

**This project is a Telegram bot built for interfacing with the RVC (Retrieval-based Voice Conversion) models. It allows users to download and interact with voice conversion models directly through a Telegram interface.**

## Features

- Download RVC models via a Python script.
- Easy-to-run Telegram bot for voice conversion tasks.
  
## Requirements

- Python 3.8+
- Install the required packages using:

  ```bash
  pip install -r requirements.txt
  ```

## How to Use

### 1. Download RVC Models

To download an RVC model, use the following command:

```bash
python src/download_model.py <model_url> <directory_name>
```

- `<model_url>`: The URL of the RVC model you want to download.
- `<directory_name>`: The name of the directory where the model will be saved.

### 2. Running the Telegram Bot

Before running the bot, make sure you have a valid Telegram bot token. You can obtain this from [BotFather](https://core.telegram.org/bots#botfather).

To run the Telegram bot, execute the following:

```bash
python src/tele_bot.py 
```

then click this link t.me/rvcconverbot and you're done ;)

## todo
- [ ] drive mounth for colab backups




## License

This project is licensed under the [MIT License](LICENSE).



(nodejs sucks for this project)
