from dotenv import load_dotenv
from os import getenv

load_dotenv()

MONGO_DSN = getenv('MONGO_DSN')
TG_BOT_TOKEN = getenv('TG_BOT_TOKEN')
DADATA_API = getenv('DADATA_API')
DADATA_SECRET = getenv('DADATA_SECRET')
