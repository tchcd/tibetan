import asyncpg
import config
import asyncio
import json


async def create_users(conn):
    sql = """DROP TABLE IF EXISTS users CASCADE;
    CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT,
    last_name TEXT,
    reg_date TIMESTAMP
    );"""
    await conn.execute(sql)


async def create_words(conn):
    sql = """DROP TABLE IF EXISTS words CASCADE;
         CREATE TABLE words (
        id SERIAL PRIMARY KEY,
        word TEXT UNIQUE,
        translation TEXT
        );"""
    await conn.execute(sql)


async def create_alphabet(conn):
    sql = """DROP TABLE IF EXISTS alphabet CASCADE;
         CREATE TABLE alphabet (
        id SERIAL PRIMARY KEY,
        letter TEXT UNIQUE,
        transcription TEXT
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
        interval INTEGER,
        force_repeat INTEGER DEFAULT 0
        );"""
    await conn.execute(sql)


async def create_score(conn):
    sql = """DROP TABLE IF EXISTS score CASCADE;
    CREATE TABLE score (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id),
    current_score INTEGER DEFAULT 0,
    first_place_count INTEGER DEFAULT 0,
    second_place_count INTEGER DEFAULT 0,
    third_place_count INTEGER DEFAULT 0
    );"""
    await conn.execute(sql)


async def run(conn):
    await create_users(conn)
    await create_words(conn)
    await create_alphabet(conn)
    await create_words_history(conn)
    await create_score(conn)


async def add_words(conn):
    with open('./initial_dict.json', 'r') as f:
        init_dict = json.load(f)
    sql = """
    INSERT INTO public.words (word, translation) VALUES($1, $2)
    """
    for key, value in init_dict.items():
        await conn.execute(sql, key, value)


async def add_alphabet(conn):
    alphabet = {'རྐ': 'ra-ka-tak-GA',
                'རྒ': 'ra-ga-tak-GA',
                'རྔ': 'ra-nga-tak-NGA',
                'རྗ': 'ra-ja-tak-JA',
                'རྙ': 'ra-nya-tak-NYA',
                'རྟ': 'ra-ta-tak-TA',
                'རྡ': 'ra-da-tak-DA',
                'རྣ': 'ra-na-tak-NA',
                'རྦ': 'ra-ba-tak-BA',
                'རྨ': 'ra-ma-tak-MA',
                'རྩ': 'ra-tsa-tak-TSA',
                'རྫ': 'ra-dza-tak-DZA',
                'ཀླ': 'ka-la-tak-LA',
                'གླ': 'ga-la-tak-LA',
                'ལྒ': 'la-ga-tak-GA',
                'ལྔ': 'la-nga-tak-NGA',
                'ལྕ': 'la-ca-tak-CA',
                'ལྗ': 'la-ja-tak-JA',
                'ལྟ': 'la-ta-tak-TA',
                'ལྡ': 'la-da-tak-DA',
                'ལྤ': 'la-pa-tak-PA',
                'ལྷ': 'la-lha-tak-LHA',
                'ལྦ': 'la-ba-tak-BA',
                'ལྐ': 'la-ka-tak-GA',
                'སྐ': 'sa-ka-tak-GA',
                'བླ': 'ba-la-tak-LA',
                'སྒ': 'sa-ga-tak-GA',
                'སྔ': 'sa-nga-tak-NGA',
                'སྙ': 'sa-nya-tak-NYA',
                'སྟ': 'sa-ta-tak-TA',
                'སྡ': 'sa-da-tak-DA',
                'སྣ': 'sa-na-tak-NA',
                'སྤ': 'sa-pa-tak-PA',
                'སྦ': 'sa-ba-tak-BA',
                'སྨ': 'sa-ma-tak-MA',
                'སྩ': 'sa-tsa-tak-TSA',
                'ཀྱ': 'ka-ya-tak-J`A',
                'རླ': 'ra-la-tak-LA',
                'གྱ': 'ga-ya-tak-JA',
                'པྱ': 'pa-ya-tak-CA',
                'ཕྱ': 'pha-ya-tak-CHA',
                'བྱ': 'ba-ya-tak-JA',
                'མྱ': 'ma-ya-tak-NYA',
                'ཧ': 'ha-ya-tak-H`YA',
                'ཀྲ': 'ka-ra-tak-T(r)A',
                'སླ': 'sa-la-tak-LA',
                'ཟླ': 'za-la-tak-DA',
                'གྲ': 'ga-ra-tak-D(r)A',
                'ཁྲ': 'kha-ra-tak-T`(r)A',
                'ཁྱ': 'kha-ya-tak-CHA',
                'ཏྲ': 'ta-ra-tak-TA',
                'ཐྲ': 'tha-ra-tak-THA',
                'དྲ': 'da-ra-tak-DA',
                'ནྲ': 'na-ra-tak-NA',
                'པྲ': 'pa-ra-tak-T(r)A',
                'ཕྲ': 'pha-ra-tak-T`(r)A',
                'བྲ': 'ba-ra-tak-D(r)A',
                'ཀྭ': 'ka-basur-KA',
                'སྲ': 'sa-ra-tak-SRA',
                'ཧྲ': 'ha-ra-tak-HRA',
                'མྲ': 'ma-ra-tak-MRA',
                'གྭ': 'ga-basur-GA',
                'ཉྭ': 'nya-basur-NYA',
                'དྭ': 'da-basur-DVA',
                'ཙྭ': 'tsa-basur-TSVA',
                'ཚྭ': 'tsha-basur-TSHVA',
                'ཞྭ': 'zha-basur-ZHA',
                'ཟྭ': 'za-basur-ZA',
                'ཤྭ': 'sha-basur-SHA',
                'ཧྭ': 'ha-basur-HA',
                'ཁྲྦྭ': 'kha-ra-tak-basur-KHA'}
    sql = """
    INSERT INTO public.alphabet (letter, transcription) VALUES($1, $2)
    """
    for key, value in alphabet.items():
        await conn.execute(sql, key, value)


async def main():
    conn = await asyncpg.connect(config.PG_CON)
    await run(conn)
    await add_words(conn)
    await add_alphabet(conn)
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
