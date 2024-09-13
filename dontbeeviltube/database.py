from contextlib import contextmanager
from typing import Any, cast

import psycopg
from psycopg.rows import namedtuple_row
from psycopg_pool import ConnectionPool

from dontbeeviltube.config import cfg


class Database:
    @staticmethod
    def _configure_conn(conn: psycopg.Connection):
        conn.row_factory = namedtuple_row
        conn.autocommit = True

    def __init__(self):
        # We cannot use NamedTuple in the Connection generic param,
        # because then the type checker insists that it is an "empty"
        # namedtuple (whatever that means) and throws a warning
        # whenever you access any attributes on it. I can't find a way
        # to annotate a namedtuple that lets you look up any attribute
        # on it, so just using Any.
        self.pool = cast(
            ConnectionPool[psycopg.Connection[Any]],
            ConnectionPool(cfg.db_addr, configure=Database._configure_conn),
        )

    @contextmanager
    def getconn(self):
        with self.pool.getconn() as conn:
            yield conn

    @contextmanager
    def cursor(self):
        with self.getconn() as conn:
            with conn.cursor() as curs:
                yield curs

    @contextmanager
    def transaction(self):
        with self.getconn() as conn:
            with conn.cursor() as curs:
                with conn.transaction():
                    yield curs


db = Database()
