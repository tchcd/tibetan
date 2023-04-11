import asyncpg
import config
from typing import NamedTuple, List, Tuple, Optional
from datetime import datetime, timedelta
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from dataclasses import dataclass

SUCCESS_SCORE_CONST = 10
FAILURE_SCORE_CONST = 5


@dataclass
class Word:
    id: int
    word: str
    translation: str
    next_attempt: datetime = '1111-11-11 00:00:00'


@dataclass
class WordHistoryAttempt:
    id: int
    user_id: int
    word: str
    last_attempt: datetime
    next_attempt: datetime
    interval: int


async def check_word_criterion(next_attempt, message):
    time_now = datetime.now()
    if next_attempt is None:
        return True
    if next_attempt > time_now:
        keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.add(KeyboardButton('/start', callback_data='start'))
        await message.answer(f"Нет новых слов для повторений. \nСледующее слово в {next_attempt} \n"
                             f"Нажмите /start и выберите тренировку", reply_markup=keyboard)
        #raise ValueError('Нет слов для повторений!')
        #return False
    else:
        return True


async def run_connection():
    conn = await asyncpg.connect(config.pg_con)
    return conn


async def close_connection(conn):
    await conn.close()


async def words_get_word(user_id: int) -> Word:
    conn = await asyncpg.connect(config.pg_con)

    word = await conn.fetchrow(
                    f"""SELECT w.id, w.word, w.translation, next_attempt
                        FROM words w
                        LEFT JOIN words_history wh on w.id=wh.word_id
                        WHERE wh.user_id = {user_id} or wh.user_id is Null
                        ORDER BY COALESCE(next_attempt, '1111-11-11') ASC LIMIT 1
                    """)
    if not word:
        word = await conn.fetchrow(
                        f"""SELECT w.id, w.word, w.translation, next_attempt
                            --NOW() AT TIME ZONE 'Europe/Moscow' as next_attempt
                            FROM words w ORDER BY random() LIMIT 1
                        """)
    print('ВЫБРАЛ СЛОВО ПОСЛЕ ЗАПРОСА', word)
    await conn.close()
    return Word(*word)


async def words_get_wrong_translation(true_word: str) -> List[tuple]:
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


async def words_get_score(user_id: str):
    conn = await asyncpg.connect(config.pg_con)
    score = await conn.fetchval(
        f"""SELECT current_score
            FROM score
            WHERE user_id = '{user_id}';
        """)
    await conn.close()
    return int(score)


async def words_check_answer(user_id, user_answer, correct_answer, message, data):
    conn = await asyncpg.connect(config.pg_con)
    score = data.get('score')
    if user_answer == correct_answer:
        await message.answer("Вы выбрали правильный ответ!")
        await add_attempt_to_history(user=user_id,
                                     word=data.get('true_word'),
                                     message=message, success=True)
        # обновить скор
        print('ПРАВИЛЬНЫЙ ОТВЕТ ОБНАВЛЯЮ СКОР')
        score += SUCCESS_SCORE_CONST
        sql = f"""UPDATE score SET current_score = $1 WHERE user_id = $2"""
        await conn.execute(sql, *[score, user_id])
        print('ПРАВИЛЬНЫЙ ОТВЕТ ОБНОВИЛ СКОР')
    else:
        await message.answer(f"Неправильный ответ! Правильный ответ: {correct_answer}")
        await add_attempt_to_history(user=user_id,
                                     word=data.get('true_word'),
                                     message=message, success=False)
        # обновить скор
        print('НЕЕ ПРАВИЛЬНЫЙ ОТВЕТ ОБНАВЛЯЮ СКОР')
        score -= FAILURE_SCORE_CONST
        if score < 0:
            score = 0
        sql = f"""UPDATE score SET current_score = $1 WHERE user_id = $2"""
        await conn.execute(sql, *[score, user_id])
        print('НЕЕ ПРАВИЛЬНЫЙ ОТВЕТ ОБНОВИЛ СКОР')
    await conn.close()


async def add_attempt_to_history(user: int, word: str, message: Message, success: bool):
    date_format = '%Y-%m-%d %H:%M:%S'
    default_interval = 3600  # one hour
    attempt = WordHistoryAttempt(id=0, user_id=0, word='',
                                 last_attempt=datetime.min, next_attempt=datetime.min,
                                 interval=0)
    attempt.last_attempt = datetime.now().replace(microsecond=0)

    print(f'ВЫБРАЛ СЛОВО {word}')


    conn = await asyncpg.connect(config.pg_con)
    attempt.user_id = user
    attempt.word_id = await conn.fetchval(
        f"""SELECT id FROM words WHERE word = '{word}'"""
    )
    if not attempt.user_id:
        await message.answer("Что-то пошло не так, нажмите /start и попробуйте снова")

    print(f'USER {attempt.user_id}, WORD_ID {attempt.word_id}')

    history_record = await conn.fetchrow(
        f"""SELECT id, interval, next_attempt FROM words_history 
        WHERE user_id = '{attempt.user_id}' AND word_id = '{attempt.word_id}'""")

    print(history_record)
    # Проверка наступила ли следующая попытка для слова

    if history_record:
        history_record = list(history_record)
        attempt.id, attempt.interval = history_record[0], history_record[1]
        attempt.interval = attempt.interval * 2 if success else attempt.interval / 3 + timedelta(seconds=1800).total_seconds()
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
        await conn.close()
    else:
        attempt.next_attempt = attempt.last_attempt + timedelta(seconds=default_interval)
        insert_row = f"""INSERT INTO words_history (user_id, word_id, last_attempt, next_attempt)
                         VALUES ($1, $2, $3, $4)
                        """
        values = [attempt.user_id, attempt.word_id,
                  attempt.last_attempt,
                  attempt.next_attempt]
        await conn.execute(insert_row, *values)
        await conn.close()



