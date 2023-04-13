from aiogram.utils import executor
from main import run
from create_bot import dp


if __name__ == "__main__":
    run(dp)
    executor.start_polling(dp, skip_updates=True)
