import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from credentials import BOT_TOKEN, BOT_USERNAME
from Database import Database
from cryption import decrypt, encrypt

class App:

    def __init__(self):
        self.configure_logging()
        application = Application.builder().token(BOT_TOKEN).build()
        self.db = Database()


        application.add_handler(CommandHandler("start", start))

        print(f"Your bot is listening! Navigate to http://t.me/{BOT_USERNAME} to interact with it!")
        
        application.run_polling(allowed_updates=Update.ALL_TYPES)


    def confiqure_loggin(self):
        # Enable logging
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
        )
        # set higher logging level for httpx to avoid all GET and POST requests being logged
        logging.getLogger("httpx").setLevel(logging.WARNING)

        logger = logging.getLogger(__name__)


    async def sign_in(update :Update, context :ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("sign in", callback_data='sign-in')]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Please choose:", reply_markup=reply_markup)


    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        keyboard = [
            [InlineKeyboardButton("get ananymous link", callback_data="1")],
            [InlineKeyboardButton("help", callback_data='2')],
        ]

        print(f'[INFO] from user: {update.message.from_user}')
        print(f'[INFO] replyed to: {update.message.reply_to_message}')

        replay_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Please choose:", reply_markup=replay_markup)


    async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query

        await query.answer()

        if (query.data == 'sign-in'):
            telegram_id = update.message.from_user.username
            
            print(f'[INFO] user {telegram_id} signed in')
            await query.edit_message_text(text="sign in")


        await query.edit_message_text(text=f"Selected option: {query.data}")
