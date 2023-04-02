import asyncpg
import config
import asyncio

async def create_users(conn):
    sql = """DROP TABLE IF EXISTS users CASCADE;
    CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    last_name VARCHAR(50),
    reg_date TIMESTAMP
    );"""
    await conn.execute(sql)


async def create_words(conn):
    sql = """DROP TABLE IF EXISTS words CASCADE;
         CREATE TABLE words (
        id SERIAL PRIMARY KEY,
        word VARCHAR(50) UNIQUE,
        translation VARCHAR(100)
        );"""
    await conn.execute(sql)


async def create_words_history(conn):
    sql = """DROP TABLE IF EXISTS words_history CASCADE;
        CREATE TABLE words_history (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        word_id INTEGER REFERENCES words(id),
        last_attempt TIMESTAMP,
        next_attempt TIMESTAMP,
        interval INTEGER
        );"""
    await conn.execute(sql)


async def create_score(conn):
    sql = """DROP TABLE IF EXISTS score CASCADE;
    CREATE TABLE score (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    current_correct_count INTEGER,
    total_correct_count INTEGER,
    first_place_count INTEGER,
    second_place_count INTEGER,
    third_place_count INTEGER
    );"""
    await conn.execute(sql)


async def run(conn):
    await create_users(conn)
    await create_words(conn)
    await create_words_history(conn)
    await create_score(conn)


async def add_rows(conn):
    dict = {
        "ས་": "земля", "ཆུ་": "вода", "མེ་": "огонь", "བོད་": "Тибет", "ཨཔ་": "отец", "ཨམ་": "мать", "ཨཁུ་": "дядя",
        "བུ་": "мальчик, сын", "བུམོ་": "девочка, дочь", "ཉིམ་": "солнце",
        "དུབ་": "дым", "ཞིམི་": "кошка", "ཞམོ་": "шапка", "ཨོམ་": "молоко", "གཞམ་": "готовить, подготавливать",
        "གསལ་": "ясный, прояснять", "མངར་": "сладкий"
    }
    sql = """
    INSERT INTO public.words (word, translation) VALUES($1, $2)
    """
    for key, value in dict.items():
        await conn.execute(sql, key, value)
    #await conn.execute(sql, **dict)


async def main():
    conn = await asyncpg.connect(config.pg_con)
    await run(conn)
    await add_rows(conn)
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
