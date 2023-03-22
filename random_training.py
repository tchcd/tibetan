import asyncpg
import config
from typing import NamedTuple, List, Tuple, Optional
from datetime import datetime, timedelta
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from dataclasses import dataclass


@dataclass
class Word:
    id: int
    word: str
    translation: str
    next_attemp: datetime


@dataclass
class WordHistoryAttempt:
    id: int
    user_id: int
    word: str
    last_attempt: datetime
    next_attempt: datetime
    interval: int



async def words_get_word(user_id: int) -> Word:
    conn = await asyncpg.connect(config.pg_con)
    word = await conn.fetchrow(
                    f"""SELECT w.id, w.word, w.translation, next_attempt
                        FROM words w
                        LEFT JOIN words_history wh on w.id=wh.word_id
                        WHERE wh.user_id = {user_id} or wh.user_id is Null
                        ORDER BY COALESCE(next_attempt, '1111-11-11') ASC LIMIT 1
                    """)
    # if not word:
    #     word = await conn.fetchrow(
    #                     f"""SELECT w.id, w.word, w.translation
    #                         FROM words w ORDER BY random() LIMIT 1
    #                     """)
    print('ВЫБРАЛ СЛОВО ПОСЛЕ ЗАПРОСА', word)
    await conn.close()
    return Word(*word)


async def words_get_wrong_translation(true_word: str) -> List[tuple]:
    conn = await asyncpg.connect(config.pg_con)
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