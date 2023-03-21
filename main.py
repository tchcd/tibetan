from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from create_bot import dp
from words_training import words_get_word, words_get_wrong_translation, add_attempt_to_history
from alphabet_training import alphabet_get_word, alphabet_get_wrong_translation
import asyncpg
import config


async def user_registration(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    await message.answer(f"Привет! \nВот тренировки которые \n"
                         f"/words - слово-перевод \n/alphabet - тренировка надписных и подписных\n"
                         f"Достижения и другие команды можно посмотреть в синем Menu")

    sql = """INSERT INTO public.users (id, name) VALUES($1, $2)"""
    conn = await asyncpg.connect(config.pg_con)
    try:
        await conn.execute(sql, *[user_id, username])
    except asyncpg.exceptions.UniqueViolationError:
        pass


async def words_send_msg(message: Message):
    user_id = message.from_user.id
    true_data = await words_get_word(user_id)
    true_word = true_data.word
    true_translation = true_data.translation

    print(f'DEBUG выбрано слово: {true_word}')
    wrong_words = await words_get_wrong_translation(true_word)
    print(f'DEBUG неверные переводы: {wrong_words}')
    print(f'DEBUG истинный перевод: {((true_translation,))}')

    answers = [word[0] for word in list(set(wrong_words + [(true_translation,)]))]

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for answer1, answer2 in zip(answers[:2], answers[2:]):
        keyboard.add(KeyboardButton(str(answer1)),
                     KeyboardButton(str(answer2)))

    await message.answer(f"Выберите правильный перевод слова: {true_word}", reply_markup=keyboard)
    message.answer_data = {'correct_answer': true_translation}

    user_data = dp.current_state(user=user_id)
    await user_data.set_data({'true_translation': true_translation,
                              'true_word': true_word,
                              'training': 'words_training'})


async def alphabet_send_msg(message: Message):

    true_data = await alphabet_get_word()
    true_word = true_data.letter
    true_translation = true_data.transcription
    user_id = message.from_user.id

    print(f'DEBUG выбрано слово: {true_word}')
    wrong_words = await alphabet_get_wrong_translation(true_word)
    print(f'DEBUG неверные переводы: {wrong_words}')
    print(f'DEBUG истинный перевод: {((true_translation,))}')

    answers = [word[0] for word in list(set(wrong_words + [(true_translation,)]))]
    # print(answers)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for answer1, answer2 in zip(answers[:2], answers[2:]):
        keyboard.add(KeyboardButton(str(answer1)),
                     KeyboardButton(str(answer2)))

    await message.answer(f"Выберите правильный перевод слова: {true_word}", reply_markup=keyboard)
    message.answer_data = {'correct_answer': true_translation}

    user_data = dp.current_state(user=user_id)
    await user_data.set_data({'true_translation': true_translation,
                              'true_word': true_word,
                              'training': 'alphabet'})


async def check_answer(message: Message):
    user_id = message.from_user.id
    user_answer = message.text
    user_data = dp.current_state(user=user_id)
    data = await user_data.get_data()
    correct_answer = data.get('true_translation')


    print('DEBUG ответ юзера:', user_answer)
    print('DEBUG корректный ответ:', correct_answer)
    if user_answer == correct_answer:
        await message.answer("Вы выбрали правильный ответ!")
        if data.get('training') == 'words_training':
            await add_attempt_to_history(user=user_id,
                                         word=data.get('true_word'),
                                         message=message, success=True)
            # обновить скор
            await words_send_msg(message)
        if data.get('training') == 'alphabet':
            await alphabet_send_msg(message)
    else:
        await add_attempt_to_history(user=user_id,
                                     word=data.get('true_word'),
                                     message=message, success=False)
        # обновить скор
        await message.answer(f"Неправильный ответ! Правильный ответ: {correct_answer}")


def run(dp):
    dp.register_message_handler(user_registration, commands=['start'])
    dp.register_message_handler(alphabet_send_msg, commands=['alphabet'])
    dp.register_message_handler(words_send_msg, commands=['words'])
    dp.register_message_handler(check_answer)
