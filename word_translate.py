# import random
# import asyncio
# from aiogram import Bot, Dispatcher
# from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
#
# # Создаем объекты бота и диспетчера
# import config
#
# bot = Bot(token=config.TOKEN)
# dp = Dispatcher(bot)
#
# # Список слов на тибетском
# #words = ["རྒྱུན"]#"མཚན", "སྣོན", "སྒྲིག", "ཡི་གེ", "མི་རིགས", "དཔར", , "གློག"]
# words = ['ལུགས་།', 'ཕར', 'ནང']
#
# # Выбираем случайное слово
# #word = random.choice(words)
#
# # создаем клавиатуру с вариантами ответа
# keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
# #keyboard = InlineKeyboardMarkup(row_width=2)
# # for i in range(4):
# #     button = KeyboardButton(words[i])
# #     #button = InlineKeyboardButton(words[i], callback_data=words[i])
# #     keyboard.add(button)
# button1 = KeyboardButton(words[0])
# button2 = KeyboardButton(words[1])
# button3 = KeyboardButton(words[2])
# button4 = KeyboardButton(words[3])
#
# # добавляем кнопки на клавиатуру
# keyboard.add(button1, button2)
# keyboard.add(button3, button4)
# # функция для выбора нового слова и отправки его пользователю
# async def send_new_word(message: Message):
#     # выбираем случайное слово из списка
#     word = random.choice(words)
#     # отправляем пользователю новое слово и клавиатуру с вариантами ответа
#     await message.answer(f"Выберите правильный перевод слова: {word}", reply_markup=keyboard)
# # Создаем список для угаданных букв
# #
# # guessed = []
# # for i in range(len(word)):
# #     guessed.append("_")
#
# # Словарь для соответствия тибетских букв и латинских символов
# tibetan_alphabet = {
#     "ཀ": "ka",
#     "ཁ": "kha",
#     "ག": "ga",
#     "ང": "nga",
#     "ཅ": "cha",
#     "ཆ": "chha",
#     "ཇ": "ja",
#     "ཉ": "nya",
#     "ཏ": "ta",
#     "ཐ": "tha",
#     "ད": "da",
#     "ན": "na",
#     "པ": "pa",
#     "ཕ": "pha",
#     "བ": "ba",
#     "མ": "ma",
#     "ཙ": "tsa",
#     "ཚ": "tsha",
#     "ཛ": "dza",
#     "ཝ": "wa",
#     "ཞ": "zha",
#     "ཟ": "za",
#     "འ": "'a",
#     "ཡ": "ya",
#     "ར": "ra",
#     "ལ": "la",
#     "ཤ": "sha",
#     "ས": "sa",
#     "ཧ": "ha",
#     "ཨ": "'a",
#    "ུ": "gigu"}
#
#
#
# # Преобразуем слово на тибетском в латинские символы
# # latin_word = ""
# # for letter in word:
# #     latin_word += tibetan_alphabet.get(letter, "")
#
# # #
# # # # Хэндлер для команды /start
# # # @dp.message_handler(commands=['start'])
# # # async def start_handler(message: types.Message):
# # #     # Выводим приветственное сообщение
# # #     await message.answer('Добро пожаловать в игру в тибетские буквы! Я загадал слово на тибетском, попробуйте угадать его буквы.')
# #
# #
# # # Хэндлер для текстовых сообщений
# # @dp.message_handler(content_types=['text'])
# # async def text_handler(message: types.Message):
# #     await message.answer(f"Напиши слово Земля")
# #     letter = message.text.lower()
# #
# #     if letter in word:
# #         await message.answer(f"Буква {letter} есть в слове: ")
# #     else:
# #         await message.answer(f"Нет буквы {letter} ")
# #     # Проверяем, является ли сообщение буквой
#     # if len(message.text) == 1 :
#     #     letter = message.text.lower()
#     #     # Проверяем, есть ли такая буква в слове
#     #     if letter in latin_word:
#     #         # Заменяем все угаданные буквы на соответствующие
#     #         for i in range(len(latin_word)):
#     #             if latin_word[i] == letter:
#     #                 guessed[i] = letter
#     #         # Проверяем, все ли буквы угаданы
#     #         if "_" not in guessed:
#     #             await message.answer(f"Вы угадали слово {word} на тибетском языке!")
#     #             return
#     #         else:
#     #             await message.answer(f"Буква {letter} есть в слове: {' '.join(guessed)}")
#     #     else:
#     #         await message.answer(f"Буквы {letter} нет в слове.")
#     # else:
#     #     await message.answer("Пожалуйста, введите одну букву.")
#
#
# async def check_answer(message: Message):
#     # получаем выбранный пользователем вариант ответа
#     user_answer = message.text
#     print(user_answer)
#     # получаем правильный ответ
#     correct_answer = random.choice(words)
#     # проверяем, совпадает ли ответ пользователя с правильным ответом
#     if user_answer == correct_answer:
#         await message.answer("Вы выбрали правильный ответ!")
#     else:
#         await message.answer(f"Неправильный ответ! Правильный ответ: {correct_answer}")
#
# dp.register_message_handler(send_new_word, commands=['start'])
# dp.register_message_handler(check_answer)
#
# # Запускаем бота
# async def main():
#     await dp.start_polling()
#
# if __name__ == '__main__':
#     asyncio.run(main())