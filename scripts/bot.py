import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from interpreter import Interpreter
import time
"""
This is a bot 

"""



def elaborate_message(message: str) -> str:
    """
    This function takes a message as input and returns a string as output.
    """

    bot = Interpreter(message)
    bot.run()
    print("sleeping 5")
    #time.sleep(5)
    response = bot.get_response()


    return response

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="""Hi there! I'm a bot that can help you planning your flight. 
                                        Ask me anything! """)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    elaborated_text = elaborate_message(update.message.text)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=elaborated_text)

if __name__ == '__main__':
    
    # Load environment variables
    load_dotenv() 

    # Create application
    application = ApplicationBuilder().token(os.getenv('FLIGHTAI_TOKEN')).build()
    
    # Add handlers
    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    
    # Add handlers to application
    application.add_handler(start_handler)
    application.add_handler(echo_handler)

    # Run application
    application.run_polling()