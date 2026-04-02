import pymysql
from pymysql.cursors import DictCursor

from gix.config import get_mysql_config


def get_connection(*, autocommit: bool | None = None):
    cfg = get_mysql_config()
    cfg = {**cfg, "cursorclass": DictCursor}
    conn = pymysql.connect(**cfg)
    if autocommit is not None:
        conn.autocommit(autocommit)
    return conn
