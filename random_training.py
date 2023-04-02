import asyncpg
import config
from typing import NamedTuple, List, Tuple, Optional
from datetime import datetime, timedelta
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from dataclasses import dataclass


@dataclass
class RandomWord:
    id: int
    word: str
    translation: str


async def random_get_word() -> RandomWord:
    conn = await asyncpg.connect(config.pg_con)
    word = await conn.fetchrow(
                            f"""SELECT w.id, w.word, w.translation
                                FROM words w ORDER BY random() LIMIT 1
                            """)
    await conn.close()
    return RandomWord(*word)


async def random_get_wrong_translation(true_word: str) -> List[tuple]:
    conn = await asyncpg.connect(config.pg_con)
    res = await conn.fetch(
        f"""SELECT translation
            FROM words
            WHERE word != '{true_word}'
            ORDER BY random()
            LIMIT 3;
        """)
    await conn.close()
    wrong_words = [tuple(row) for row in res]
    return wrong_words


async def random_check_answer(user_answer, correct_answer, message):
    if user_answer == correct_answer:
        await message.answer("Вы выбрали правильный ответ!")
    else:
        await message.answer(f"Неправильный ответ! Правильный ответ: {correct_answer}")