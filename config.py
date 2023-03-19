from typing import NamedTuple


class DbConn(NamedTuple):
    dbname: str
    host: str
    user: str
    password: str
    port: str

pg_con = 'postgresql://postgres:qqwweerrttyy11@localhost/tibetan2'
TOKEN = "6175652151:AAH9daZwDkDJzQ87O-uHUFTL7IVAnOtlj6I"
#pg_con = DbConn(dbname='tibetan2', host='localhost', user='postgress', password='qqwweerrttyy11', port=5432)
