"""Wait for MySQL, then apply schema (idempotent). Used by Docker entrypoint."""
import os
import sys
import time
from pathlib import Path

# Running as `python docker/wait_and_init.py` puts `docker/` on sys.path — add project root.
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pymysql


def wait_mysql() -> None:
    host = os.environ.get("MYSQL_HOST", "mysql")
    port = int(os.environ.get("MYSQL_PORT", "3306"))
    user = os.environ.get("MYSQL_USER", "root")
    password = os.environ.get("MYSQL_PASSWORD", "")
    for attempt in range(60):
        try:
            conn = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                connect_timeout=5,
            )
            conn.close()
            print("MySQL is reachable.", flush=True)
            return
        except Exception as e:
            print(f"Waiting for MySQL ({attempt + 1}/60): {e}", flush=True)
            time.sleep(2)
    print("MySQL did not become ready in time.", flush=True)
    sys.exit(1)


def run_init() -> None:
    from init_db import main as init_main

    init_main()


if __name__ == "__main__":
    wait_mysql()
    run_init()
