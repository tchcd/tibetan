#import random
#import asyncio
#from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
#from aiogram.contrib.fsm_storage.memory import MemoryStorage
#from aiogram.utils import executor
import asyncpg
#import config
#import sqlalchemy as sa
#import app

from typing import NamedTuple, List, Tuple, Optional
from datetime import datetime
from create_bot import dp


class Word(NamedTuple):
    id: int
    word: str
    translation: str
    last_attempt: datetime
    next_attempt: datetime
    interval: int


async def words_get_word() -> Word:
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


async def words_get_wrong_translation(true_word: str) -> List[tuple]:
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


# async def words_check_answer(message: Message):
#     user_answer = message.text
#     user_data = dp.current_state(user=message.from_user.id)
#     data = await user_data.get_data()
#     correct_answer = data.get('true_translation')
#
#     #print('DEBUG ответ юзера:', user_answer)
#     #print('DEBUG корректный ответ:', correct_answer)
#     if user_answer == correct_answer:
#         await message.answer("Вы выбрали правильный ответ!")
#         #await words_send_msg(message)
#     else:
#         await message.answer(f"Неправильный ответ! Правильный ответ: {correct_answer}")

