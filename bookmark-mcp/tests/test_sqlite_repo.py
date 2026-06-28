"""SQLite BookmarkRepository 单元测试

使用临时文件 DB（隔离测试环境），覆盖核心方法。
"""
import os
import sys
import tempfile
from pathlib import Path
from typing import Iterator

import pytest


# 必须先设环境变量（config 在 import 时读）
import os
import sys
from pathlib import Path

# 测试 DB 路径（与 conftest 保持一致）
TEST_DB_PATH = Path(tempfile.mkdtemp(prefix="bm_test_")) / "test_bookmarks.db"
os.environ["SQLITE_PATH"] = str(TEST_DB_PATH)
os.environ["DATA_BACKEND"] = "sqlite"

# 加载 admin 项目（repository 在那里）
ADMIN_DIR = Path(__file__).resolve().parent.parent.parent / "bookmark-manager-admin"
sys.path.insert(0, str(ADMIN_DIR))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# 加载 server-v4（触发 config 读取）
import importlib.util
spec = importlib.util.spec_from_file_location(
    "server_v4", Path(__file__).resolve().parent.parent / "server-v4.py"
)
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)

# conftest.py 提供 `repo` fixture 和自动 cleanup


# ============================================================================
# Helper
# ============================================================================

def _sample_bookmark(idx: int = 0) -> dict:
    """生成测试用书签"""
    return {
        "url": f"https://test{idx}.com/path{idx}",
        "title": f"Test Bookmark {idx}",
        "tags": [f"tag{idx}", "common"],
        "category": "测试" if idx % 2 == 0 else "开发",
        "folder_path": f"folder/subfolder{idx}",
    }


# ============================================================================
# Test 1: count
# ============================================================================

@pytest.mark.unit
def test_count_empty(repo):
    """空 DB 时 count = 0"""
    assert repo.count() == 0


@pytest.mark.unit
def test_count_after_inserts(repo):
    """插入后 count 正确"""
    for i in range(5):
        repo.create(_sample_bookmark(i))
    assert repo.count() == 5


@pytest.mark.unit
def test_count_by_source(repo):
    """按 source 字段计数"""
    # 3 条 chrome-extension
    for i in range(3):
        bm = _sample_bookmark(i)
        bm["source"] = "chrome-extension"
        repo.create(bm)
    # 2 条 manual
    for i in range(3, 5):
        bm = _sample_bookmark(i)
        bm["source"] = "manual"
        repo.create(bm)

    assert repo.count_by_source("chrome-extension") == 3
    assert repo.count_by_source("manual") == 2
    assert repo.count_by_source("nonexistent") == 0


# ============================================================================
# Test 2: find_all
# ============================================================================

@pytest.mark.unit
def test_find_all_basic(repo):
    """基本 find_all 返回所有书签"""
    for i in range(3):
        repo.create(_sample_bookmark(i))
    items = repo.find_all(limit=10)
    assert len(items) == 3
    assert all("url" in b for b in items)
    assert all("tags" in b for b in items)  # tags 字段填充


@pytest.mark.unit
def test_find_all_with_category_filter(repo):
    """按分类过滤"""
    for i in range(4):
        repo.create(_sample_bookmark(i))  # i=0,2 → 测试；i=1,3 → 开发
    items = repo.find_all(category="测试")
    assert len(items) == 2
    assert all(b["category"] == "测试" for b in items)


@pytest.mark.unit
def test_find_all_with_tag_filter(repo):
    """按 tag 过滤"""
    for i in range(3):
        repo.create(_sample_bookmark(i))  # tag0/tag1/tag2 + common
    items = repo.find_all(tag="common")
    assert len(items) == 3  # 三条都有 common

    items = repo.find_all(tag="tag1")
    assert len(items) == 1


@pytest.mark.unit
def test_find_all_with_search(repo):
    """关键字搜索（title/url 模糊匹配）"""
    for i in range(3):
        repo.create(_sample_bookmark(i))
    items = repo.find_all(search="Test Bookmark 1")
    assert len(items) == 1
    assert "Test Bookmark 1" in items[0]["title"]


# ============================================================================
# Test 3: create + 幂等性
# ============================================================================

@pytest.mark.unit
def test_create_and_find_by_url_hash(repo):
    """插入后能用 url_hash 查回"""
    bm = _sample_bookmark(0)
    repo.create(bm)
    found = repo.find_by_url_hash(repo._normalize(bm)["url_hash"])
    assert found is not None
    assert found["title"] == "Test Bookmark 0"


@pytest.mark.unit
def test_create_dedup_by_url_hash(repo):
    """相同 url 重复插入只算一条"""
    repo.create(_sample_bookmark(0))
    repo.create(_sample_bookmark(0))  # 同样的 url
    assert repo.count() == 1


@pytest.mark.unit
def test_create_returns_dict_with_tags(repo):
    """create 返回的 dict 包含 tags 数组"""
    bm = _sample_bookmark(0)
    result = repo.create(bm)
    assert "tags" in result
    assert "tag0" in result["tags"]
    assert "common" in result["tags"]


# ============================================================================
# Test 4: bulk_create（sync 场景）
# ============================================================================

@pytest.mark.unit
def test_bulk_create_stats(repo):
    """bulk_create 返回 {added, skipped, errors}"""
    items = [_sample_bookmark(i) for i in range(5)]
    stats = repo.bulk_create(items)
    assert stats["added"] == 5
    assert stats["skipped"] == 0
    assert stats["errors"] == 0


@pytest.mark.unit
def test_bulk_create_dedup(repo):
    """bulk_create 自动去重"""
    items = [_sample_bookmark(i) for i in range(3)]
    items.append(_sample_bookmark(0))  # 重复
    items.append(_sample_bookmark(1))  # 重复
    stats = repo.bulk_create(items)
    assert stats["added"] == 3
    assert stats["skipped"] == 2


@pytest.mark.unit
def test_bulk_create_with_source_chrome_extension(repo):
    """Chrome 扩展同步：source 应保留为 chrome-extension"""
    items = [_sample_bookmark(0)]
    items[0]["source"] = "chrome-extension"
    repo.bulk_create(items)
    assert repo.count_by_source("chrome-extension") == 1


# ============================================================================
# Test 5: get_last_sync_time
# ============================================================================

@pytest.mark.unit
def test_get_last_sync_time_empty(repo):
    """空 DB 返回 None"""
    assert repo.get_last_sync_time() is None


@pytest.mark.unit
def test_get_last_sync_time_returns_max_updated_at(repo):
    """返回最大 updated_at（不是 created_at）"""
    repo.create(_sample_bookmark(0))
    last = repo.get_last_sync_time()
    assert last is not None
    # 应该有 ISO8601 格式
    assert "T" in last
    assert last.endswith("Z")


# ============================================================================
# Test 6: 极端场景
# ============================================================================

@pytest.mark.unit
def test_create_unicode_title(repo):
    """Unicode 标题 + 中文 tags 正确存储"""
    bm = {
        "url": "https://中文.com/path",
        "title": "中文标题：测试 🎉",
        "tags": ["中文", "测试", "AI"],
        "category": "未分类",
    }
    result = repo.create(bm)
    assert "中文" in result["title"]
    assert "测试" in result["tags"]


@pytest.mark.unit
def test_delete_by_url_hash(repo):
    """按 url_hash 删除"""
    bm = _sample_bookmark(0)
    repo.create(bm)
    h = repo._normalize(bm)["url_hash"]
    assert repo.delete_by_url_hash(h) is True
    assert repo.count() == 0


# ============================================================================
# 关闭时清理
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    """测试结束后清理临时 DB"""
    yield
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()