import asyncpg
from typing import NamedTuple, List
from dataclasses import dataclass
import config

@dataclass
class Letter:
    id: int
    letter: str
    transcription: str


async def alphabet_get_word() -> Letter:
    conn = await asyncpg.connect(config.pg_con)
    res = await conn.fetchrow(
                        """SELECT id, letter, transcription
                           FROM alphabet ORDER BY random() LIMIT 1
                        """)
    await conn.close()
    return Letter(*res)


async def alphabet_get_wrong_translation(true_word: str) -> List[tuple]:
    conn = await asyncpg.connect(config.pg_con)
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