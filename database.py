import asyncpg


class Database:
    def __init__(self, uri):
        self.uri = uri
        self.connection = None

    async def __aenter__(self):
        self.connection = await asyncpg.connect(self.uri)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.connection.close()

    async def get_new_word(self, user_id):
        new_word = await self.connection.fetchrow(
                        f"""
                        SELECT w.id, w.word, w.translation, 0 as force_repeat, '1111-11-11 00:00:00' as next_attempt
                        FROM words w
                        WHERE id = (
                            SELECT id FROM(
                            SELECT id FROM words
                            EXCEPT 
                            SELECT word_id FROM words_history
                            WHERE user_id = {user_id}
                            )t
                            ORDER BY RANDOM() LIMIT 1
                        )
                        """)
        return new_word

    async def get_force_word(self, user_id):
        force_word = await self.connection.fetchrow(
                    f"""SELECT w.id, w.word, w.translation, force_repeat, next_attempt
                                    FROM words w
                                    LEFT JOIN words_history wh on w.id=wh.word_id
                                    WHERE wh.user_id = {user_id} AND force_repeat = 1
                                    LIMIT 1
                                """)
        return force_word

    async def get_main_word(self, user_id):
        main_word = await self.connection.fetchrow(
            f"""SELECT w.id, w.word, w.translation, force_repeat, next_attempt
                                FROM words w
                                LEFT JOIN words_history wh on w.id=wh.word_id
                                WHERE wh.user_id = {user_id}
                                ORDER BY COALESCE(next_attempt, '1111-11-11 00:00:00') ASC
                                LIMIT 1
                            """)
        return main_word

    async def check_is_force_list_empty(self, user_id):
        word = await self.connection.fetchrow(
            f"""SELECT w.id, w.word, w.translation, force_repeat, next_attempt
                                FROM words w
                                LEFT JOIN words_history wh on w.id=wh.word_id
                                WHERE wh.user_id = {user_id} 
                                AND force_repeat = 1
                                LIMIT 1
                            """)
        return word

    async def get_wrong_translations(self, true_word):
        res = await self.connection.fetch(
            f"""SELECT translation
                    FROM words
                    WHERE word != '{true_word}'
                    ORDER BY random()
                    LIMIT 3;
                """)
        return res

    async def get_score(self, user_id):
        score = await self.connection.fetchval(
            f"""SELECT current_score
                    FROM score
                    WHERE user_id = '{user_id}';
                """)
        return score

