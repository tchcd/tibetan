import asyncpg
import config
from typing import NamedTuple, List, Tuple, Optional
from datetime import datetime


class Word(NamedTuple):
    id: int
    word: str
    translation: str
    last_attempt: datetime
    next_attempt: datetime
    interval: int


async def words_get_word() -> Word:
    conn = await asyncpg.connect(config.pg_con)
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