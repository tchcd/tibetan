
from aiogram.utils import executor

#from alphabet import alphabet, alphabet_send_msg,check_answer
from main import run
from create_bot import dp

FLAG = 0

run(dp)
#translate_word.translate_words(dp)
executor.start_polling(dp, skip_updates=True)




# Запуск бота
#if __name__ == "__main__":
