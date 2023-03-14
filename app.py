from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from translate_word import translate_word
from alphabet import alphabet
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio
import config


bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
loop = asyncio.get_event_loop()
#db = Database(loop)


translate_word(dp, storage)
#alphabet(dp)

# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)