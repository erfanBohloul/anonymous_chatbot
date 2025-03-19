import os

if os.path.exists('.env'):
    from dotenv import load_dotenv
    load_dotenv()

else:
    raise Exception("no .env file found")

BOT_TOKEN= os.getenv("BOT_TOKEN")
BOT_USERNAME= os.getenv('BOT_USERNAME')
AES_KEY= os.getenv('AES_KEY')