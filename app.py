
from aiogram.utils import executor

#from alphabet import alphabet, send_new_word,check_answer
from handlers import alphabet, translate_word
from create_bot import dp

alphabet.alphabets(dp)
#translate_word.translate_words(dp)
executor.start_polling(dp, skip_updates=True)

#
# async def on_start(message: types.Message, state):
#     await message.reply("Привет! Я бот для выполнения команд /alphabet и /translate_word.")
#     async with state.proxy() as data:
#         data['name'] = message.text
#     print(data['name'])
#     alphabet(dp, storage)
#     translate_word(dp, storage)
    # if message.text =='/alphabet':
    #     alphabet(dp, storage)
    # elif  message.text =='/translate_word':
    #     translate_word(dp, storage)
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
#dp.register_message_handler(on_start, commands=['start', 'hello'])



# Запуск бота
#if __name__ == "__main__":
