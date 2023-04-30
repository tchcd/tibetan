from aiogram.utils import executor
from main import run
from create_bot import dp, bot
import asyncio
import asyncpg
from datetime import datetime
import config
import pytz

tz = pytz.timezone('Europe/Moscow')


async def check_time():
    while True:
        now = datetime.now(tz)
        if now.weekday() == 4 and now.hour == 20 and now.minute == 00:
            conn = await asyncpg.connect(config.PG_CON)
            get_winner_q = """SELECT user_id, rnk, name from (
                              SELECT *, dense_rank() over(order by current_score desc) as rnk 
                              FROM score s
                              LEFT JOIN users u on s.user_id = u.id
                              )t
                              WHERE rnk <= 3
                              ORDER BY rnk"""
            awards_first_place = "UPDATE score SET first_place_count = first_place_count + 1 WHERE user_id in ($1)"
            awards_second_place = "UPDATE score SET second_place_count = second_place_count + 1 WHERE user_id in ($1)"
            awards_third_place = "UPDATE score SET third_place_count = third_place_count + 1 WHERE user_id in ($1)"
            clear_score_q = "UPDATE score SET current_score = 0 WHERE 1=1"

            users_rank = await conn.fetch(get_winner_q)
            users = []
            for row in users_rank:
                row = tuple(row)
                if row[1] == 1:
                    users.append((row[2], '🥇'))
                    await conn.execute(awards_first_place, row[0])
                elif row[1] == 2:
                    users.append((row[2], '🥈'))
                    await conn.execute(awards_second_place, row[0])
                elif row[1] == 3:
                    users.append((row[2], '🥉'))
                    await conn.execute(awards_third_place, row[0])
            celebrate_msg = f'<b>Поздравляем победителей этой недели!</b>\n'
            users_str = '\n'.join([f'{user[0]}: {user[1]}' for user in users])
            await bot.send_message(config.CHAT_BOT_ID, celebrate_msg+users_str, parse_mode='HTML')
            await conn.execute(clear_score_q)
            await conn.close()
        await asyncio.sleep(60)


async def start_checking_on_startup(dp):
    asyncio.create_task(check_time())

if __name__ == "__main__":
    run(dp)
    executor.start_polling(dp, on_startup=start_checking_on_startup, skip_updates=True)
