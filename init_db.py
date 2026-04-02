"""
Create MySQL database (if needed) and tables from database/schema.sql.
Usage (from project root): python init_db.py
Set MYSQL_* in .env (see .env.example).
"""

from pathlib import Path

import pymysql

from gix.config import get_mysql_config


def main():
    schema_path = Path(__file__).resolve().parent / "database" / "schema.sql"
    sql = schema_path.read_text(encoding="utf-8")

    cfg = dict(get_mysql_config())
    cfg.pop("cursorclass", None)
    dbname = cfg.get("database")
    conn = pymysql.connect(**{k: v for k, v in cfg.items() if k != "database"})
    try:
        with conn.cursor() as cur:
            if dbname:
                cur.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{dbname}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
                cur.execute(f"USE `{dbname}`")
            for stmt in _statements(sql):
                cur.execute(stmt)
        conn.commit()
        print("Schema applied OK.")
    finally:
        conn.close()


def _statements(text: str) -> list[str]:
    lines = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("--"):
            continue
        lines.append(line)
    full = "\n".join(lines)
    return [s.strip() for s in full.split(";") if s.strip()]


if __name__ == "__main__":
    main()
