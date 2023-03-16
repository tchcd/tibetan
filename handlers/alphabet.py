import random
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton,ReplyKeyboardRemove
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
import asyncpg
import config
import sqlalchemy as sa
from create_bot import dp, bot

from typing import NamedTuple, List, Tuple, Optional
from datetime import datetime

# bot = Bot(token=config.TOKEN)
# dp = Dispatcher(bot, storage=MemoryStorage())
# loop = asyncio.get_event_loop()
#db = Database(loop)


metadata = sa.MetaData()

# table_dict = sa.Table(
#     "dict",
#     metadata,
#     sa.Column("id", sa.Integer, primary_key=True),
#     sa.Column("word", sa.String(255)),
#     sa.Column("translation", sa.String(255))
# )
#
class Word(NamedTuple):
    id: int
    letter: str
    transcription: str


async def get_word() -> Word:
    conn = await asyncpg.connect('postgresql://postgres:qqwweerrttyy11@localhost/tibetan2')
    # res = await conn.fetchrow(
    #                 """SELECT id, word, translation, last_attempt, next_attempt, interval
    #                    FROM dict ORDER BY next_attempt ASC LIMIT 1
    #                 """)
    res = await conn.fetchrow(
                        """SELECT id, letter, transcription
                           FROM alphabet ORDER BY random() LIMIT 1
                        """)
    await conn.close()
    return Word(*res)


async def get_wrong_translation(true_word: str) -> List[tuple]:
    conn = await asyncpg.connect('postgresql://postgres:qqwweerrttyy11@localhost/tibetan2')
    res = await conn.fetch(
        f"""SELECT transcription
            FROM alphabet
            WHERE letter != '{true_word}'
            ORDER BY random()
            LIMIT 3;
        """)
    await conn.close()
    wrong_words = [tuple(row) for row in res]
    return wrong_words


async def send_new_word(message: Message):
    true_data = await get_word()
    true_word = true_data.letter
    true_translation = true_data.transcription

    print(f'DEBUG выбрано слово: {true_word}')
    wrong_words = await get_wrong_translation(true_word)
    print(f'DEBUG неверные переводы: {wrong_words}')
    print(f'DEBUG истинный перевод: {((true_translation,))}')

    answers = [word[0] for word in list(set(wrong_words + [(true_translation,)]))]
    # print(answers)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for answer1, answer2 in zip(answers[:2], answers[2:]):
        keyboard.add(KeyboardButton(str(answer1)),
                     KeyboardButton(str(answer2)))

    await message.answer(f"Выберите правильный перевод слова: {true_word}", reply_markup=keyboard)
    message.answer_data = {'correct_answer': true_translation}

    user_data = dp.current_state(user=message.from_user.id)
    await user_data.set_data({'true_translation': true_translation})

    #user_answer = message.text
    #print('DEBUG ответ юзера:', user_answer)
    #if user_answer == true_translation:
    #    await message.answer("Вы выбрали правильный ответ!")
    #    await send_new_word(message)
    #else:
    #    await message.answer(f"Неправильный ответ! Правильный ответ: {true_translation}")


async def check_answer_word(message: Message):
    # получаем выбранный пользователем вариант ответа
    user_answer = message.text
    user_data = dp.current_state(user=message.from_user.id)
    data = await user_data.get_data()
    correct_answer = data.get('true_translation')

    print('DEBUG ответ юзера:', user_answer)
    print('DEBUG корректный ответ:', correct_answer)
    if user_answer == correct_answer:
        await message.answer("Вы выбрали правильный ответ!")
        print(dp.storage)
        print(dp.current_state().__dict__)
        #await send_new_word(message)
    else:
        await message.answer(f"Неправильный ответ! Правильный ответ: {correct_answer}")
    if user_answer == 'q':
        print('hui')
        await bot.session.close()
        raise ValueError


# async def cancel_handler(message: Message, state):
#     """
#     Allow user to cancel any action
#     """
#     #current_state = await state.get_state()
#     #if current_state is None:
#
#
#     #await state.finish()
#     # And remove keyboard (just in case)
#     await message.reply('Cancelled.', reply_markup=ReplyKeyboardRemove())
#     return

# def alphabet(dp, storage: MemoryStorage):
#     dp.register_message_handler(lambda message: cancel_handler(message, dp), Text(equals="q"))
#     dp.register_message_handler(lambda message: send_new_word(message, dp), commands=['alphabet'])
#     dp.register_message_handler(lambda message: check_answer(message, dp))
#
#     dp.storage = storage

from handlers.translate_word import send_new_translate_word, check_answer_translate


def alphabets(dp):
    dp.register_message_handler(send_new_word, commands=['alphabet'])
    dp.register_message_handler(send_new_translate_word, commands=['hello'])
    dp.register_message_handler(check_answer_word)

    #dp.register_message_handler(check_answer_translate)
    #dp.register_message_handler(cancel_handler, Text(equals="q"))

    #dp.storage = storage

#
# # Запускаем бота
# if __name__ == '__main__':
#     executor.start_polling(dp, skip_updates=True)
