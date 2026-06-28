"""bookmark-mcp 核心逻辑测试

覆盖 3 个高风险回归点：
1. _is_browser_running 不能误报 Electron 应用（macOS pgrep bug 修复）
2. _flatten_chrome_tree 必须保留嵌套 folder_path
3. sync_from_chrome 的 dry_run 模式不调用 admin
"""
import asyncio
import importlib.util
import json
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# 加载 server-v4.py（文件名带连字符，需要 importlib）
# ---------------------------------------------------------------------------

MCP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(MCP_DIR))


def _load_server():
    spec = importlib.util.spec_from_file_location(
        "server_v4", MCP_DIR / "server-v4.py"
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


server = _load_server()


# ===========================================================================
# Test 1: _is_browser_running 不能误报 Electron 应用
# ===========================================================================

def _fake_pgrep(stdout: str, returncode: int = 0):
    """构造 pgrep subprocess.run 返回值（带 args 属性，避免真实代码访问抛错）"""
    from types import SimpleNamespace
    return SimpleNamespace(stdout=stdout, returncode=returncode, args=["pgrep", "-f", "..."])


@pytest.mark.unit
def test_is_browser_running_不误报_Electron_app(monkeypatch):
    """macOS 下 pgrep -f "chrome" 会匹配 Electron 应用的 chrome_crashpad_handler。

    Bug 复现：如果用宽匹配 pgrep，会把百度网盘/Marvis/VSCode 等的
    chrome_crashpad_handler 误认为 Chrome 进程。

    修复后：必须用精确路径匹配 /Applications/Google Chrome.app/...
    """
    # 模拟"只有 Electron 应用在跑"的情况
    fake_pgrep_output = (
        "1091 /Applications/BaiduNetdisk_mac.app/.../chrome_crashpad_handler\n"
        "2179 /Applications/Marvis.app/.../chrome_crashpad_handler\n"
        "20234 /Applications/Visual Studio Code.app/.../chrome_crashpad_handler\n"
    )

    def fake_run(*args, **kwargs):
        cmd_args = args[0] if args else kwargs.get("args", [])
        if any("Google Chrome.app/Contents/MacOS" in str(a) for a in cmd_args):
            return _fake_pgrep("")  # 精确匹配 Chrome 路径 → 没命中
        return _fake_pgrep(fake_pgrep_output)

    monkeypatch.setattr(server.subprocess, "run", fake_run)
    monkeypatch.setattr(server.platform, "system", lambda: "Darwin")

    result = server._is_browser_running("chrome")
    assert result is False, (
        "_is_browser_running 误把 Electron 应用当作 Chrome（pgrep 匹配逻辑太宽）"
    )


@pytest.mark.unit
def test_is_browser_running_正确检测_Chrome_主进程(monkeypatch):
    """当 Chrome 真的在跑时，必须返回 True。"""
    fake_pgrep_output = "1234 /Applications/Google Chrome.app/Contents/MacOS/Google Chrome\n"

    def fake_run(*args, **kwargs):
        return _fake_pgrep(fake_pgrep_output)

    monkeypatch.setattr(server.subprocess, "run", fake_run)
    monkeypatch.setattr(server.platform, "system", lambda: "Darwin")

    assert server._is_browser_running("chrome") is True


@pytest.mark.unit
def test_is_browser_running_Linux_下正确检测(monkeypatch):
    """Linux 下用精确路径 /opt/google/chrome/chrome 匹配。"""
    fake_pgrep_output = "5678 /opt/google/chrome/chrome\n"

    def fake_run(*args, **kwargs):
        return _fake_pgrep(fake_pgrep_output)

    monkeypatch.setattr(server.subprocess, "run", fake_run)
    monkeypatch.setattr(server.platform, "system", lambda: "Linux")

    assert server._is_browser_running("chrome") is True


@pytest.mark.unit
def test_is_browser_running_无匹配时返回_false(monkeypatch):
    """没有任何匹配时必须返回 False（不是抛异常或 None）。"""
    def fake_run(*args, **kwargs):
        return _fake_pgrep("", returncode=1)

    monkeypatch.setattr(server.subprocess, "run", fake_run)
    monkeypatch.setattr(server.platform, "system", lambda: "Darwin")

    assert server._is_browser_running("chrome") is False


# ===========================================================================
# Test 2: _flatten_chrome_tree 保留嵌套 folder_path
# ===========================================================================

@pytest.mark.unit
def test_flatten_chrome_tree_保留嵌套_folder_path():
    """书签的 folder_path 必须反映完整嵌套结构。"""
    sample_tree = {
        "roots": {
            "bookmark_bar": {
                "name": "书签栏",
                "children": [
                    {
                        "type": "folder",
                        "name": "技术",
                        "children": [
                            {
                                "type": "folder",
                                "name": "前端",
                                "children": [
                                    {
                                        "type": "url",
                                        "url": "https://react.dev",
                                        "name": "React 官网",
                                    },
                                ],
                            },
                            {
                                "type": "url",
                                "url": "https://github.com",
                                "name": "GitHub",
                            },
                        ],
                    },
                ],
            },
            "other": {
                "name": "其他书签",
                "children": [
                    {
                        "type": "url",
                        "url": "https://example.com",
                        "name": "示例",
                    },
                ],
            },
        },
    }

    flat = server._flatten_chrome_tree(sample_tree["roots"])

    assert len(flat) == 3, f"应有 3 条书签，实际 {len(flat)}"

    # React 应该在最深嵌套
    react = next((b for b in flat if "react" in b["url"]), None)
    assert react is not None
    assert react["folder_path"] == "书签栏/技术/前端", (
        f"嵌套 folder_path 应为 '书签栏/技术/前端'，实际 {react['folder_path']!r}"
    )

    # GitHub 在二级嵌套
    github = next((b for b in flat if "github.com" in b["url"]), None)
    assert github is not None
    assert github["folder_path"] == "书签栏/技术"

    # 顶层示例
    example = next((b for b in flat if "example.com" in b["url"]), None)
    assert example is not None
    assert example["folder_path"] == "其他书签"


@pytest.mark.unit
def test_flatten_chrome_tree_跳过_invalid_url():
    """非 http(s) 的条目必须被跳过。"""
    sample_tree = {
        "roots": {
            "bookmark_bar": {
                "name": "书签栏",
                "children": [
                    {"type": "url", "url": "https://valid.com", "name": "Valid"},
                    {"type": "url", "url": "javascript:alert(1)", "name": "JS"},
                    {"type": "url", "url": "ftp://old.com", "name": "FTP"},
                    {"type": "url", "url": "", "name": "Empty"},
                    {"type": "url", "url": "https://no-title.com", "name": ""},
                ],
            },
        },
    }
    flat = server._flatten_chrome_tree(sample_tree["roots"])
    assert len(flat) == 1, f"只应保留 https 的有效条目，实际 {flat}"
    assert flat[0]["url"] == "https://valid.com"


# ===========================================================================
# Test 3: sync_from_chrome dry_run 不调用 admin
# ===========================================================================

@pytest.mark.unit
def test_sync_from_chrome_dry_run_不调用_admin(monkeypatch, tmp_path):
    """dry_run=true 时应该只读取 + 解析，不发任何 HTTP 请求到 admin。"""
    # 1. 写一个假的 Bookmarks JSON
    fake_bookmarks = {
        "roots": {
            "bookmark_bar": {
                "name": "书签栏",
                "children": [
                    {"type": "url", "url": "https://a.com", "name": "A"},
                    {"type": "url", "url": "https://b.com", "name": "B"},
                ],
            },
        },
    }
    fake_file = tmp_path / "Bookmarks"
    fake_file.write_text(json.dumps(fake_bookmarks), encoding="utf-8")

    # 2. mock _detect_profiles 返回我们的假 profile（用 server 模块里的 BrowserProfile）
    fake_profile = server.BrowserProfile(
        name="Chrome (Default)",
        os_path=str(tmp_path),
        profile="Default",
        bookmarks_file=str(fake_file),
    )

    monkeypatch.setattr(server, "_detect_profiles", lambda b: [fake_profile])
    monkeypatch.setattr(server, "_is_browser_running", lambda b: False)

    # 3. mock admin 调用，如果被调用则测试失败
    call_count = {"n": 0}

    async def fake_call_api(*args, **kwargs):
        call_count["n"] += 1
        return {"status": "success", "data": {"stats": {"added": 99}}}

    monkeypatch.setattr(server, "_call_api", fake_call_api)

    # 4. 跑 dry_run（FastMCP 装饰的 async 函数本身就是可调用的，无需 .fn）
    result = asyncio.run(server.sync_from_chrome(
        browser="chrome", profile="Default", dry_run=True
    ))

    # 5. 验证
    assert call_count["n"] == 0, (
        f"dry_run 模式不应调用 admin，实际调用了 {call_count['n']} 次"
    )
    assert result["dry_run"] is True
    assert result["total_read"] == 2
    assert result["browser_running"] is False


@pytest.mark.unit
def test_sync_from_chrome_检测浏览器在跑时_立即报错(monkeypatch, tmp_path):
    """当浏览器在跑时，必须立即返回错误，不能读取 Bookmarks（避免数据损坏）。"""
    monkeypatch.setattr(server, "_detect_profiles", lambda b: [
        server.BrowserProfile(
            name="Chrome (Default)",
            os_path=str(tmp_path),
            profile="Default",
            bookmarks_file=str(tmp_path / "Bookmarks"),
        ),
    ])
    monkeypatch.setattr(server, "_is_browser_running", lambda b: True)

    result = asyncio.run(server.sync_from_chrome(
        browser="chrome", profile="Default"
    ))

    assert result["status"] == "error"
    assert result["browser_running"] is True
    assert "关闭" in result["error"] or "关闭浏览器" in result["tip"]


# ===========================================================================
# conftest
# ===========================================================================

@pytest.fixture(scope="session")
def server_module():
    """复用 server 模块（避免每个 test 重新 import）"""
    return server