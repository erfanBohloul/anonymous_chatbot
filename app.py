import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Bot
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from credentials import BOT_TOKEN, BOT_USERNAME
from database import Database
from cryption import decrypt, encrypt

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


bot = Bot(token=BOT_TOKEN)
application = Application.builder().token(BOT_TOKEN).build()
db = Database()



async def sign_in(update :Update, context :ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.username

    # check if user exists already
    if user_exist(user):
        await update.message.reply_text("You have already signed in.")
        return
    
    # if not add it
    add_user(user)
    await update.message.reply_text("You are now signed in.")


async def get_link(update :Update, context :ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user.username
    logger.info(f"in get_link func: username={user}")

    # check if user has signed in
    if not user_exist(user):
        await update.message.reply_text("You need to sign in first.")
        return
    
    # get link
    encrypted_username = encrypt(user)
    link = create_link(encrypted_username)

    await update.message.reply_text(f'{link}')

async def chat(update :Update, context :ContextTypes.DEFAULT_TYPE) -> None:
    
    logger.info(f"here in chat func update:\n{update}")
    return


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass


def create_link(username :str):
    return f'https://t.me/ananymous_zrb_bot?chat={username}'


def user_exist(telegram_id :str) -> bool:
    encrypted_username = encrypt(telegram_id)
    return not Database().find_user_by_name(encrypted_username) is None

def add_user(telegram_id :str):
    encrypted_username = encrypt(telegram_id)
    Database().add_user(encrypted_username)



application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("signin", sign_in))
application.add_handler(CommandHandler("get_link", get_link))
application.add_handler(CommandHandler("chat", chat))

print(f"Your bot is listening! Navigate to http://t.me/{BOT_USERNAME} to interact with it!")

application.run_polling(allowed_updates=Update.ALL_TYPES)