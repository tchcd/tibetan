from os import environ
from os.path import join, dirname
from dotenv import load_dotenv


def get_from_env(key):
    dotenv_path = join(dirname(__file__), ".env")
    load_dotenv(dotenv_path)
    return environ.get(key)


DB_PASSWORD = get_from_env('DB_PASSWORD')
DB_USER = get_from_env('DB_USER')
DB_SCHEMA = get_from_env('DB_SCHEMA')
PG_CON = get_from_env('pg_con')
TOKEN = get_from_env('TG_TOKEN')
FEEDBACK_CHAT = get_from_env('CHAT_ID')
CHAT_BOT_ID = get_from_env('CHAT_BOT_ID')
