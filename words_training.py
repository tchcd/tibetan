from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import asyncpg
import config

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


# async def words_send_msg(message: Message):
#     true_data = await words_get_word()
#     true_word = true_data.word
#     true_translation = true_data.translation
#
#     # print(f'DEBUG выбрано слово: {true_word}')
#     wrong_words = await words_get_wrong_translation(true_word)
#     #print(f'DEBUG неверные переводы: {wrong_words}')
#     #print(f'DEBUG истинный перевод: {((true_translation,))}')
#
#     answers = [word[0] for word in list(set(wrong_words + [(true_translation,)]))]
#
#     keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
#     for answer1, answer2 in zip(answers[:2], answers[2:]):
#         keyboard.add(KeyboardButton(str(answer1)),
#                      KeyboardButton(str(answer2)))
#
#     await message.answer(f"Выберите правильный перевод слова: {true_word}", reply_markup=keyboard)
#     message.answer_data = {'correct_answer': true_translation}
#
#     user_data = dp.current_state(user=message.from_user.id)
#     await user_data.set_data({'true_translation': true_translation})
#
#     if message.text.startswith('/'):
#         return
#
#
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
#         await words_send_msg(message)
#     else:
#         await message.answer(f"Неправильный ответ! Правильный ответ: {correct_answer}")

