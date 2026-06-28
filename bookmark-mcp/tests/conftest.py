"""pytest conftest — 共享 fixture + SQLite 初始化"""
import os
import sys
import sqlite3
import tempfile
from pathlib import Path

import pytest

# 测试 DB 路径
TEST_DB_DIR = Path(tempfile.mkdtemp(prefix="bm_test_"))
TEST_DB_PATH = TEST_DB_DIR / "test_bookmarks.db"
os.environ["SQLITE_PATH"] = str(TEST_DB_PATH)
os.environ["DATA_BACKEND"] = "sqlite"

# 加 admin 路径
ADMIN_DIR = Path(__file__).resolve().parent.parent.parent / "bookmark-manager-admin"
sys.path.insert(0, str(ADMIN_DIR))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# admin 的 schema.sql
ADMIN_SCHEMA = ADMIN_DIR / "app" / "db" / "schema.sql"


def _init_schema(db_path: str) -> None:
    """从 schema.sql 初始化表"""
    sql = ADMIN_SCHEMA.read_text(encoding="utf-8")
    conn = sqlite3.connect(db_path)
    conn.executescript(sql)
    conn.commit()
    conn.close()


@pytest.fixture
def repo():
    """每个测试前重置 BookmarkRepository + 重建表"""
    from app.repositories.bookmark_repo import BookmarkRepository
    import app.repositories.bookmark_repo as repo_module
    # 1. 重置单例
    repo_module._repo = None
    # 2. 清掉所有可能的 thread-local 连接（通过新建实例强制丢弃）
    BookmarkRepository._local = type(BookmarkRepository._local)()
    # 3. 删 DB 文件
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    for ext in ["-wal", "-shm", "-journal"]:
        p = Path(str(TEST_DB_PATH) + ext)
        if p.exists():
            p.unlink()
    # 4. 重建表
    _init_schema(str(TEST_DB_PATH))
    return BookmarkRepository(db_path=str(TEST_DB_PATH))


@pytest.fixture(autouse=True)
def _cleanup_test_db():
    """每个测试后清理 DB"""
    yield
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()