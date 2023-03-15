from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from translate_word import translate_word
from alphabet import alphabet, send_new_word,check_answer
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio
import config


bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
loop = asyncio.get_event_loop()
#db = Database(loop)



dp.add_handler(CommandHandler("alphabet", alphabet_handler))
dp.add_handler(CommandHandler("translate_word", translate_word_handler))
#
async def on_start(message: types.Message):
    await message.reply("Привет! Я бот для выполнения команд /alphabet и /translate_word.")
    if message.text =='/alphabet':
        alphabet(dp, storage)
    elif  message.text =='/translate_word':
        translate_word(dp, storage)
#
# @dp.message_handler(commands=['alphabet'])
# async def alphabet_handler(message: types.Message):
#     #await alphabet(dp, storage, message)
#     await send_new_word(message, dp)
#     await check_answer(message, dp)
#
# @dp.message_handler(commands=['translate_word'])
# async def translate_word_handler(message: types.Message):
#     await translate_word(dp, storage, message)
#
dp.register_message_handler(on_start, commands=['start', 'alphabet', 'hello'])

# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)