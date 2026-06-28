"""SQLite schema 加载工具（给 pytest 用的简化版）"""
import sqlite3
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parent.parent.parent / "bookmark-manager-admin" / "app" / "db" / "schema.sql"


def init_schema(db_path: str) -> None:
    """初始化 SQLite schema（从 schema.sql 读取）"""
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    conn = sqlite3.connect(db_path)
    conn.executescript(sql)
    conn.commit()
    conn.close()