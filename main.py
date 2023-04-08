from create_bot import dp, bot
from words_training import words_get_word, words_get_wrong_translation,\
    add_attempt_to_history, check_word_criterion, words_check_answer, words_get_score
from alphabet_training import alphabet_get_word, alphabet_get_wrong_translation, alphabet_check_answer
from random_training import *
import asyncpg
import config


async def user_registration(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    await message.answer(f"Привет! \nВыберите тренировку:\n"
                         f"/words - слово-перевод с баллами. Каждый правильный ответ +10 баллов, неправильный -5 баллов\n"
                         f"Правильный и не правильный ответы изменяют время до следующего повторения слова.\n"
                         f"/alphabet - тренировка надписных и подписных\n"
                         f"/random - тренировка слово-перевод для случайных слов. Без начисления балов.\n"
                         f"/feedback - Обратная связь и сообщения об ошибках. \n"
                         f"/score - Достижения\n\n"
                         f"Все команды можно посмотреть в синем меню")

    user_reg = """INSERT INTO public.users (id, name) VALUES($1, $2)"""
    score_reg = """INSERT INTO public.score (user_id) VALUES($1)"""
    conn = await asyncpg.connect(config.pg_con)
    try:
        await conn.execute(user_reg, *[user_id, username])
    except asyncpg.exceptions.UniqueViolationError:
        pass
    try:
        await conn.execute(score_reg, *[user_id])
    except asyncpg.exceptions.UniqueViolationError:
        pass
    await conn.close()


async def words_send_msg(message: Message):
    user_id = message.from_user.id


    true_data = await words_get_word(user_id)
    if not await check_word_criterion(true_data.next_attemp, message):
        return
    conn = await asyncpg.connect(config.pg_con)
    score = await words_get_score(conn, user_id)
    await conn.close()
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
                              'score':score,
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


async def random_send_msg(message: Message):
    true_data = await random_get_word()
    true_word = true_data.word
    true_translation = true_data.translation
    user_id = message.from_user.id

    wrong_words = await random_get_wrong_translation(true_word)

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
                              'training': 'random'})


async def feedback(message: Message):
    await message.answer(f"Отправьте сообщение с исправлением. Укажите слово и ошибку/перевод в свободном формате")
    user_id = message.from_user.id
    username = message.from_user.username
    user_data = dp.current_state(user=user_id)
    await user_data.set_data({'username': username,
                              'training': 'feedback'})


async def check_answer(message: Message):
    user_id = message.from_user.id
    user_answer = message.text
    user_data = dp.current_state(user=user_id)
    data = await user_data.get_data()
    correct_answer = data.get('true_translation')

    if data.get('training') == 'words_training':
        await words_check_answer(user_id, user_answer, correct_answer, message, data)
        await words_send_msg(message)
    elif data.get('training') == 'alphabet':
        await alphabet_check_answer(user_answer, correct_answer, message)
        await alphabet_send_msg(message)
    elif data.get('training') == 'random':
        await random_check_answer(user_answer, correct_answer, message)
        await random_send_msg(message)
    elif data.get('training') == 'feedback':
        username = data.get('username')
        feedback_msg = f'{username}\n{user_answer}'
        await bot.send_message(config.FEEDBACK_CHAT, feedback_msg)
    else:
        await message.answer(f"Что-то пошло не так! Нажмите /start и попробуйте снова! :)")



def run(dp):
    dp.register_message_handler(user_registration, commands=['start'])
    dp.register_message_handler(alphabet_send_msg, commands=['alphabet'])
    dp.register_message_handler(words_send_msg, commands=['words'])
    dp.register_message_handler(random_send_msg, commands=['random'])
    dp.register_message_handler(feedback, commands=['feedback'])
    dp.register_message_handler(check_answer)
    #dp.register_callback_query_handler(process_callback_button1, lambda inline_query: True)
