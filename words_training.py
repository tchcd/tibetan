import asyncpg
import config
from typing import NamedTuple, List, Tuple, Optional
from datetime import datetime, timedelta
from aiogram.types import Message
from dataclasses import dataclass


@dataclass
class Word:
    id: int
    word: str
    translation: str


@dataclass
class WordHistoryAttempt:
    id: int
    user_id: int
    word_id: int
    last_attempt: datetime
    next_attempt: datetime
    interval: int


async def check_word_criterion(next_attempt, message):
    print('ВЫЗВАЛ ФУНКЦИЮ')
    if next_attempt > datetime.now():
        await message.answer("Нет новых слов для повторений. Приходите позже :)")
    else:
        await message.answer("КАКОЙ ТО ТЕСТ КАКОЙ ТО ТЕСТ КАКОЙТ ОЕТЕСЬ")


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
    next_attempt = word[-1]

    await conn.close()
    return Word(*word[:-1])


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


async def add_attempt_to_history(user: int, word: str, message: Message, success: bool):
    date_format = '%Y-%m-%d %H:%M:%S'
    default_interval = 3600  # one hour
    attempt = WordHistoryAttempt(id=0, user_id=0, word_id=0,
                                 last_attempt=datetime.min, next_attempt=datetime.min,
                                 interval=0)
    attempt.last_attempt = datetime.now().replace(microsecond=0)

    print(f'ВЫБРАЛ СЛОВО {word}')

    conn = await asyncpg.connect(config.pg_con)
    attempt.user_id = await conn.fetchval(
           f"""SELECT id FROM users WHERE id = '{user}' LIMIT 1""")
    attempt.word_id = await conn.fetchval(
            f"""SELECT id FROM words WHERE word = '{word}' LIMIT 1""")
    if not attempt.user_id:
       await message.answer("Что-то пошло не так, нажмите /start и попробуйте снова")

    print(f'USER {attempt.user_id}, WORD {attempt.word_id}')

    history_record = await conn.fetchrow(
        f"""SELECT id, interval FROM words_history 
        WHERE user_id = '{attempt.user_id}' AND word_id = '{attempt.word_id}'""")

    if history_record:
        attempt.id, attempt.interval = list(history_record.values())
        attempt.interval = attempt.interval * 2 if success else max(attempt.interval // 3, 1)
        attempt.next_attempt = attempt.last_attempt + timedelta(seconds=attempt.interval)

        if attempt.next_attempt > attempt.last_attempt + timedelta(days=30):
            attempt.next_attempt = attempt.last_attempt + timedelta(days=30)
            max_data = attempt.last_attempt + timedelta(days=30)
            attempt.interval = (max_data - attempt.last_attempt).total_seconds()
            print('INTERVAAAl', attempt.interval)

        update_row = f"""UPDATE words_history SET 
                                last_attempt = $1,
                                next_attempt = $2,
                                interval = $3
                         WHERE user_id = {attempt.user_id}
                         AND word_id = {attempt.word_id}
                                """
        values = [attempt.last_attempt,
                  attempt.next_attempt,
                  attempt.interval]
        await conn.execute(update_row, *values)

    else:
        attempt.next_attempt = attempt.last_attempt + timedelta(seconds=default_interval)
        insert_row = f"""INSERT INTO words_history (user_id, word_id, last_attempt, next_attempt)
                         VALUES ($1, $2, $3, $4)
                        """
        values = [attempt.user_id, attempt.word_id,
                  attempt.last_attempt,
                  attempt.next_attempt]
        await conn.execute(insert_row, *values)


