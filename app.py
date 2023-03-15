from aiogram import Bot, Dispatcher, types
from aiogram import executor
from translate_word import translate_word
from alphabet import alphabet, send_new_word,check_answer
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import config
from aiogram import Router

def main():
    bot = Bot(token=config.TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.start_polling(bot)



alphabet(dp, storage)
translate_word(dp, storage)



# Запуск бота
if __name__ == "__main__":
    asyncio.run(main())

