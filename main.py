from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from create_bot import dp
from words_training import words_get_word, words_get_wrong_translation
from alphabet_training import alphabet_get_word, alphabet_get_wrong_translation


async def words_send_msg(message: Message):
    true_data = await words_get_word()
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

    user_data = dp.current_state(user=message.from_user.id)
    await user_data.set_data({'true_translation': true_translation, 'flag': 10})


async def alphabet_send_msg(message: Message):
    true_data = await alphabet_get_word()
    true_word = true_data.letter
    true_translation = true_data.transcription

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

    user_data = dp.current_state(user=message.from_user.id)
    await user_data.set_data({'true_translation': true_translation, 'flag': 20})


async def check_answer(message: Message):
    user_answer = message.text
    user_data = dp.current_state(user=message.from_user.id)
    data = await user_data.get_data()
    correct_answer = data.get('true_translation')

    print('DEBUG ответ юзера:', user_answer)
    print('DEBUG корректный ответ:', correct_answer)
    if user_answer == correct_answer:
        await message.answer("Вы выбрали правильный ответ!")
        if data.get('flag') == 10:
            await words_send_msg(message)
        if data.get('flag') == 20:
            await alphabet_send_msg(message)
    else:
        await message.answer(f"Неправильный ответ! Правильный ответ: {correct_answer}")


def run(dp):
    dp.register_message_handler(alphabet_send_msg, commands=['alphabet'])
    dp.register_message_handler(words_send_msg, commands=['words'])
    dp.register_message_handler(check_answer)
