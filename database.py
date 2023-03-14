import asyncio
import asyncpg

import config

class Database:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.pool = loop.run_until_complete(
            asyncpg.create_pool(
                user='postgres',
                password='qqwweerrttyy11',
                host='localhost',
                port='5432'
            )
        )

    @staticmethod
    def formar_args(sql, parameters: dict):
        sql += ' AND '.join([
            f'{item} = ${num}' for num, item in enumerate(parameters, start=1)
        ])
        return sql, tuple(parameters.values())

    async def add_user(self, id: int, name: str):
        sql = " INSERT INTO users (id, name) VALUES ($1, $2)"
        await self.pool.execute(sql, id, name)