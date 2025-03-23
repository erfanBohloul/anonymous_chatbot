import logging, re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Bot, Message
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

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



async def sign_in(update :Update, context :ContextTypes.DEFAULT_TYPE) -> None:
    username = update.message.from_user.id
    logging.info(f'User with username: {username} wants to sign in.')

    # check if user exists already
    if user_exist(username):
        await update.message.reply_text("You have already signed in.")
        return
    
    # if not add it
    add_user(username)
    await update.message.reply_text("You are now signed in.")


async def get_link(update :Update, context :ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    logger.info(f"in get_link func: username={user_id}")

    # check if user has signed in
    if not user_exist(user_id):
        await update.message.reply_text("You need to sign in first.")
        return
    
    # get link
    encrypted_username = encrypt(user_id)
    link = create_link(encrypted_username)

    await update.message.reply_text(f'{link}')


async def chat(update :Update, context :ContextTypes.DEFAULT_TYPE) -> None:
    
    logger.info(f"here in chat func update:\n{update}")
    return


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    
    if len(args) < 1:
        await update.message.reply_text("Not enogh arg.")
        return
    
    receiver_id = args[0]
    sender_id = update.message.from_user.id

    # check if receiver_name exist
    if not user_exist(receiver_id):
        await update.message.reply_text("Username that you provided doesn't exist in our database.")
        return
    

    # check if sender_name exist
    if not user_exist(sender_id):
        await update.message.reply_text("Sign in first")
        return
    
    if str(sender_id) == str(receiver_id):
        await update.message.reply_text("You can't message yourself.")
        return
    
    msg = f"You can now chat anonumously. please reply to this message and then send messages to {receiver_id} user."
    replay = await update.message.reply_text(msg)
    
    # store replay to database as root message
    Database().add_message(replay.id, BOT_USERNAME, Database().find_user_by_name(receiver_id)[0], msg)
    return


def create_link(username :str):
    return f'https://t.me/ananymous_zrb_bot?start={username}'


def user_exist(telegram_id :str) -> bool:
    encrypted_username = encrypt(telegram_id)
    return not Database().find_user_by_name(encrypted_username) is None


def message_exist(message_id :int):
    return not Database().find_message_by_id(message_id) is None


def add_user(telegram_id :str):
    encrypted_username = encrypt(telegram_id)
    Database().add_user(encrypted_username)


def is_root_message(message :Message):
    sender = Database().get_sender_id_by_message_id(message.id)
    return str(sender) == BOT_USERNAME


def get_receiver_from_root_message(message :Message):
    text = message.text
            
    pattern = r"^You can now chat anonumously\. please reply to this message and then send messages to ([0-9]+) user\.$"
    regex = re.compile(pattern)
    match = regex.match(text)

    if match:
        receiver_name = match.group(1)
        return receiver_name
    
    else:
        return None


async def send_msg_to_receiver(sender_id :str, receiver_id :str, msg :str) -> None:
    await bot.send_message(receiver_id, f'from {sender_id}:\n{msg}')


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    replied_message = update.message.reply_to_message
    message = update.message
    sender_name = update.message.from_user.id

    receiver_name = str()
    if is_root_message(replied_message):
        receiver_name = get_receiver_from_root_message(replied_message)
        if receiver_name is None:
            raise Exception("Invalid root")
    
    else:
        receiver_id = Database().get_receiver_id_by_message_id(replied_message.id)
        receiver_name = Database().find_user_by_id(receiver_id)[1]
        if receiver_name == sender_name:
            receiver_id = Database().get_sender_id_by_message_id(replied_message.id)
            receiver_name = Database().find_user_by_id(receiver_id)[1]

        

    if receiver_name is None:
        raise Exception("Somthing wend wrong; Invalid receiver")

    logger.info(f'receiver: {receiver_name} sender: {sender_name}')
    sender_id = Database().find_user_by_name(sender_name)[0]
    receiver_id = Database().find_user_by_name(receiver_name)[0]
    Database().add_message(message.id, sender_id, receiver_id, message.text)
    await send_msg_to_receiver(receiver_name, message.text)

    await update.message.reply_text("sent")
    

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    # check if this message has replied on anything. if not it's an error
    if update.message.reply_to_message is None:
        await update.message.reply_text("Command Not found.")
        return
    
    replied_message = update.message.reply_to_message
    # check if replied message is in our database. if it's not it's an error
    if not message_exist(replied_message.id):
        await update.message.reply_text("Command not found. (Maybe replied on wrong message)")
        return
    
    # then it should be the resumbtion of some chat
    await chat(update, context)



application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("signin", sign_in))
application.add_handler(CommandHandler("get_link", get_link))
application.add_handler(CommandHandler("chat", chat))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print(f"Your bot is listening! Navigate to http://t.me/{BOT_USERNAME} to interact with it!")

application.run_polling(allowed_updates=Update.ALL_TYPES)