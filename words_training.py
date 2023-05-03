import asyncpg
import config
from typing import List
from datetime import datetime, timedelta
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from dataclasses import dataclass
from database import Database as db
import random
import pytz
import sys

SUCCESS_SCORE_CONST = 10
FAILURE_SCORE_CONST = 5
tz = pytz.timezone('Europe/Moscow')


@dataclass
class Word:
    id: int
    word: str
    translation: str
    force_repeat: int
    next_attempt: datetime = datetime.min

    def __post_init__(self):
        if isinstance(self.next_attempt, str):
            self.next_attempt = datetime.strptime(self.next_attempt, "%Y-%m-%d %H:%M:%S")


@dataclass
class WordHistoryAttempt:
    id: int
    user_id: int
    word: str
    last_attempt: datetime
    next_attempt: datetime
    interval: int
    force_repeat: int

    def __post_init__(self):
        if isinstance(self.last_attempt, str):
            self.last_attempt = datetime.strptime(self.last_attempt, "%Y-%m-%d %H:%M:%S")
        if isinstance(self.next_attempt, str):
            self.next_attempt = datetime.strptime(self.next_attempt, "%Y-%m-%d %H:%M:%S")


async def is_force_repeat_empty(user_id) -> bool:
    async with db(config.PG_CON) as conn:
        word = await conn.check_is_force_list_empty(user_id=user_id)
    return bool(not word)


async def check_word_criterion(user_id, next_attempt, force_repeat, message):
    time_now = datetime.now()
    if next_attempt is None:
        return True
    if next_attempt > time_now and force_repeat == 0 and await is_force_repeat_empty(user_id):
        keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.add(KeyboardButton('/start', callback_data='start'))
        await message.answer(f"Нет новых слов для повторений. \n"
                             f"Следующее слово в {tz.localize(next_attempt).strftime('%Y-%m-%d %H:%M:%S')}\n"
                             f"Нажмите /start и выберите тренировку", reply_markup=keyboard)
    else:
        return True


async def get_word_by_schedule(user_id):
    choice = random.randint(1, 3)
    async with db(config.PG_CON) as conn:
        word = await conn.get_main_word(user_id=user_id)
    if Word(*word).next_attempt > datetime.now() or choice == 3:
        async with db(config.PG_CON) as conn:
            force_word = await conn.get_force_word(user_id=user_id)
        if force_word:
            return Word(*force_word)
        else:
            return Word(*word)
    else:
        return Word(*word)


async def get_not_shown_word(user_id):
    async with db(config.PG_CON) as conn:
        word = await conn.get_new_word(user_id=user_id)
    if word:
        choice = random.randint(1, 3)
        if choice != 3:
            return Word(*word)
        else:
            async with db(config.PG_CON) as conn:
                force_word = await conn.get_force_word(user_id=user_id)
            if force_word:
                return Word(*force_word)
            else:
                return Word(*word)


async def words_get_word(user_id: int) -> Word:
    word = await get_not_shown_word(user_id)
    if not word:
        word = await get_word_by_schedule(user_id)
    return word


async def words_get_wrong_translation(true_word: str) -> List[tuple]:
    async with db(config.PG_CON) as conn:
        res = await conn.get_wrong_translations(true_word)
    wrong_words = [tuple(row) for row in res]
    return wrong_words


async def words_get_score(user_id: str):
    async with db(config.PG_CON) as conn:
        score = await conn.get_score(user_id)
    return int(score)


async def words_check_answer(user_id, user_answer, correct_answer, message, data):
    conn = await asyncpg.connect(config.PG_CON)
    score = data.get('score')
    if user_answer == correct_answer:
        await message.answer("Вы выбрали правильный ответ!")
        await add_attempt_to_history(user=user_id,
                                     word=data.get('true_word'),
                                     message=message, success=True)
        score += SUCCESS_SCORE_CONST
        sql = f"""UPDATE score SET current_score = $1 WHERE user_id = $2"""
        await conn.execute(sql, *[score, user_id])
    else:
        await message.answer(f"Неправильный ответ! Правильный ответ: {correct_answer}")
        await add_attempt_to_history(user=user_id,
                                     word=data.get('true_word'),
                                     message=message, success=False)
        score -= FAILURE_SCORE_CONST
        if score < 0:
            score = 0
        sql = f"""UPDATE score SET current_score = $1 WHERE user_id = $2"""
        await conn.execute(sql, *[score, user_id])
    await conn.close()


async def add_attempt_to_history(user: int, word: str, message: Message, success: bool):
    default_interval = 3600  # 1 hour
    attempt = WordHistoryAttempt(id=0, user_id=0, word='',
                                 last_attempt=datetime.min, next_attempt=datetime.min,
                                 interval=0, force_repeat=999)
    attempt.last_attempt = datetime.now().replace(microsecond=0)
    attempt.force_repeat = 0 if success else 1
    conn = await asyncpg.connect(config.PG_CON)
    attempt.user_id = user
    attempt.word_id = await conn.fetchval(
        f"""SELECT id FROM words WHERE word = '{word}'"""
    )
    if not attempt.user_id:
        await message.answer("Что-то пошло не так, нажмите /start и попробуйте снова")

    history_record = await conn.fetchrow(
        f"""SELECT id, interval, next_attempt FROM words_history 
        WHERE user_id = '{attempt.user_id}' AND word_id = '{attempt.word_id}'""")

    if history_record:
        history_record = list(history_record)
        attempt.id, attempt.interval = history_record[0], history_record[1]
        attempt.interval = attempt.interval * 2 if success else attempt.interval / 3 + timedelta(seconds=900).total_seconds()
        attempt.next_attempt = attempt.last_attempt + timedelta(seconds=attempt.interval)

        if attempt.next_attempt > attempt.last_attempt + timedelta(days=14):
            attempt.next_attempt = attempt.last_attempt + timedelta(days=14)
            max_data = attempt.last_attempt + timedelta(days=14)
            attempt.interval = (max_data - attempt.last_attempt).total_seconds()

        update_row = f"""UPDATE words_history SET 
                                last_attempt = $1,
                                next_attempt = $2,
                                interval = $3,
                                force_repeat = $4
                         WHERE user_id = {attempt.user_id}
                         AND word_id = {attempt.word_id}
                                """
        values = [attempt.last_attempt,
                  attempt.next_attempt,
                  attempt.interval,
                  attempt.force_repeat]
        await conn.execute(update_row, *values)
        await conn.close()
    else:
        attempt.interval = default_interval
        attempt.next_attempt = attempt.last_attempt + timedelta(seconds=default_interval)
        insert_row = f"""INSERT INTO words_history (user_id, word_id, last_attempt, next_attempt, interval, force_repeat)
                         VALUES ($1, $2, $3, $4, $5, $6)
                        """
        values = [attempt.user_id, attempt.word_id,
                  attempt.last_attempt, attempt.next_attempt,
                  attempt.interval, attempt.force_repeat]
        await conn.execute(insert_row, *values)
        await conn.close()



