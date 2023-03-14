import random
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

import asyncpg
import config
import sqlalchemy as sa

from typing import NamedTuple, List, Tuple, Optional
from datetime import datetime




metadata = sa.MetaData()

table_dict = sa.Table(
    "dict",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("word", sa.String(255)),
    sa.Column("translation", sa.String(255))
)

class Word(NamedTuple):
    id: int
    word: str
    translation: str
    last_attempt: datetime
    next_attempt: datetime
    interval: int


async def get_word() -> Word:
    conn = await asyncpg.connect('postgresql://postgres:qqwweerrttyy11@localhost/tibetan2')
    # res = await conn.fetchrow(
    #                 """SELECT id, word, translation, last_attempt, next_attempt, interval
    #                    FROM dict ORDER BY next_attempt ASC LIMIT 1
    #                 """)
    res = await conn.fetchrow(
                        """SELECT id, word, translation, last_attempt, next_attempt, interval
                           FROM dict ORDER BY random() LIMIT 1
                        """)
    await conn.close()
    return Word(*res)


async def get_wrong_translation(true_word: str) -> List[tuple]:
    conn = await asyncpg.connect('postgresql://postgres:qqwweerrttyy11@localhost/tibetan2')
    res = await conn.fetch(
        f"""SELECT translation
            FROM public.dict
            WHERE word != '{true_word}'
            ORDER BY random()
            LIMIT 3;
        """)
    await conn.close()
    wrong_words = [tuple(row) for row in res]
    return wrong_words


async def send_new_word(message: Message, dp: Dispatcher):
    true_data = await get_word()
    true_word = true_data.word
    true_translation = true_data.translation

    # print(f'DEBUG выбрано слово: {true_word}')
    wrong_words = await get_wrong_translation(true_word)
    # print(f'DEBUG неверные переводы: {wrong_words}')
    # print(f'DEBUG истинный перевод: {((true_translation,))}')

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


async def check_answer(message: Message, dp: Dispatcher):
    # получаем выбранный пользователем вариант ответа
    user_answer = message.text
    user_data = dp.current_state(user=message.from_user.id)
    data = await user_data.get_data()
    correct_answer = data.get('true_translation')

    print('DEBUG ответ юзера:', user_answer)
    if user_answer == correct_answer:
        await message.answer("Вы выбрали правильный ответ!")
        await send_new_word(message, dp)
    else:
        await message.answer(f"Неправильный ответ! Правильный ответ: {correct_answer}")


async def play_handler(message: Message, dp):
    await send_new_word(message, dp)
    await dp.storage.set_state(user=message.from_user.id, state="translate")


# def translate_word(dp):
#     dp.register_message_handler(send_new_word, commands=['start'])
#     dp.register_message_handler(check_answer)

def translate_word(dp, storage: MemoryStorage):
    dp.register_message_handler(play_handler, commands=['start'], state="*")
    dp.register_message_handler(check_answer, state="playing")
    dp.storage = storage


# # Запускаем бота
# if __name__ == '__main__':
#     executor.start_polling(dp, skip_updates=True)
