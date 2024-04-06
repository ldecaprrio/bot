#!/usr/bin/python3https://aka.ms/vscode-faq-old-windows
from typing import Final
import io
import argparse
from yadsl import YADSL
from PIL import Image
import requests
import telegram
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update
bot_token = '7103941002:AAF5sZUEEzZ2AG8qo4fB4oEq4H4UzLmbJqE'
chat_id = '1586118773'
def print_image_as_ascii(image_path, width=100) -> Image:
    image = Image.open(image_path)
    image = image.resize((width, int(width * image.height / image.width)))
    return image


async def send_image_to_telegram_bot(image, bot_token, chat_id):
    bot = telegram.Bot(token=bot_token)
    byte_stream = io.BytesIO()
    image.save(byte_stream, format='PNG')
    byte_stream.seek(0)
    await bot.send_photo(chat_id=chat_id, photo=byte_stream)

TOKEN: Final = '7103941002:AAF5sZUEEzZ2AG8qo4fB4oEq4H4UzLmbJqE'
BOT_USERNAME: Final = '@ynetbalance_bot'
# State constants
STATE_USERNAME = 1
STATE_PASSWORD = 2
STATE_NUMBERS = 3  # Define the state for numbers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! Thanks for chatting with me! I am a ynetbalance_bot!')
    await update.message.reply_text('Please enter your username:')
    # Set the conversation state to username
    context.user_data['state'] = STATE_USERNAME
yd = None
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global yd  # Use the global keyword to access the yd variable
    if 'state' not in context.user_data:
        # If the state is not set, assume it's the start of the conversation
        await start_command(update, context)
        return

    state = context.user_data['state']

    if state == STATE_USERNAME:
        username = update.message.text
        context.user_data['username'] = username
        await update.message.reply_text(f'Your username is {username}.')
        await update.message.reply_text('Please enter your password:')
        # Set the conversation state to password
        context.user_data['state'] = STATE_PASSWORD
    elif state == STATE_PASSWORD:
        password = update.message.text
        await update.message.reply_text(f'Your password is {password}.')
        # Process the password as needed
        # Reset the conversation state
        del context.user_data['state']

        # Authenticate using YADSL
        username = context.user_data.get('username')
        print ("username",username)
        if username:
            yd = YADSL(username=username, password=password)
            print (('yd'),yd)
            print("Login:", yd.login())
            captcha_image = print_image_as_ascii(io.BytesIO(yd.fetch_captcha()), 70)
            
            await send_image_to_telegram_bot(captcha_image, bot_token, chat_id)
            await update.message.reply_text('Please enter the numbers shown in the image:')
            # Set the conversation state to wait for response
            context.user_data['state'] = STATE_NUMBERS  # Define a new state for numbers

            
        else:
            print("Error: Username not found.")
    elif state == STATE_NUMBERS:
        numbers = update.message.text
        
        print("Numbers entered by user:", numbers)
        print (str(numbers).strip())
        print (('yd'),yd)
        verify_code = numbers.strip()
        print("Verify: ", yd.verify(verify_code))
        data_output = ""
        for k, v in yd.fetch_data().items():
            print(k, v, sep=": ")
            data_output += f'{k}: {v}\n'
        bot = telegram.Bot(token=bot_token)
        await bot.send_message(chat_id=chat_id, text=data_output)

        # Process the numbers as needed

        # Reset the conversation state
        del context.user_data['state']

    else:
        # Invalid state, reset the conversation
        await start_command(update, context)
async def error (update: Update, context: ContextTypes. DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')
if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token (TOKEN).build()
    # Commands
    app.add_handler (CommandHandler('start', start_command))
   # Messages
    app.add_handler (MessageHandler(filters. TEXT, handle_message))
  
    # Errors
    app.add_error_handler(error)
    # Polls the bot
    print('Polling...')
    app.run_polling (poll_interval=3)
    
