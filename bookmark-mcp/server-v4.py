#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bookmark Manager MCP Server v4

v4 修正：不再自造清洗逻辑，直接调用 admin 已有端点
- 复用 /v1/bookmarks/deduplicate（去重）
- 复用 /v1/scripts/analyze（分析）
- 复用 /v1/scripts/parse（解析 HTML）
- 复用 /v1/ai/suggest（AI 建议）
- 复用 /v1/tags/batch-generate（批量生成 tag）
- 复用 /v1/tags/<id>/merge（tag 合并）

v3 分类工具保留（嵌套层级 + 优先级）
"""

import os
import logging
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

import httpx
from mcp.server.fastmcp import FastMCP

# 默认指向 FastAPI :9002（Flask :9001 仍可访问，作为回退）
BOOKMARK_API_BASE = os.environ.get(
    "BOOKMARK_API_BASE",
    "http://localhost:9002/v1"
)
REQUEST_TIMEOUT = float(os.environ.get("BOOKMARK_TIMEOUT", "30"))

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("bookmark-mcp")

mcp = FastMCP(
    "Bookmark Manager",
    instructions="Bookmark MCP v4 - 完整查询/操作/分类/清洗（复用 admin 现有端点）",
)

client = httpx.AsyncClient(
    base_url=BOOKMARK_API_BASE,
    timeout=REQUEST_TIMEOUT,
    headers={
        "Content-Type": "application/json",
        # JWT token（从环境变量读，admin 默认）
        "Authorization": f"Bearer {os.environ.get('BOOKMARK_TOKEN', '')}"
    },
)


async def _call_api(method, path, *, params=None, json_body=None, files=None):
    """统一 API 调用（支持文件上传）"""
    try:
        if files:
            # 文件上传模式
            resp = await client.request(method, path, files=files)
        else:
            resp = await client.request(method, path, params=params, json=json_body)
        resp.raise_for_status()
        return {"status": "success", "data": resp.json()}
    except httpx.HTTPStatusError as e:
        return {"status": "error", "error": f"API {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ============================================================================
# v1 工具（保留）
# ============================================================================


@mcp.tool()
async def list_bookmarks(
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    """列出书签（按时间倒序，分页）

    Args:
        limit: 返回数量上限（1-500，默认 50）
        offset: 跳过前 N 条（默认 0）
    """
    return await _call_api("GET", "/bookmarks", params={"limit": min(limit, 500), "offset": max(offset, 0)})


@mcp.tool()
async def search_bookmarks(keyword: str, limit: int = 30) -> Dict[str, Any]:
    """关键字搜索

    Args:
        keyword: 搜索关键字（必填，非空）
        limit: 返回数量上限（1-200，默认 30）
    """
    if not keyword.strip():
        return {"status": "error", "error": "keyword 不能为空"}
    return await _call_api("GET", "/bookmarks", params={"q": keyword, "limit": min(limit, 200)})


@mcp.tool()
async def get_bookmarks_by_tag(tag: str, limit: int = 50) -> Dict[str, Any]:
    """按 tag 查（推荐，索引快）

    Args:
        tag: tag 名称
        limit: 返回数量上限（1-200，默认 50）
    """
    return await _call_api("GET", f"/bookmarks/tag/{tag}", params={"limit": min(limit, 200)})


@mcp.tool()
async def get_bookmarks_by_category(category: str, limit: int = 50) -> Dict[str, Any]:
    """按分类查（支持多层级路径如 "技术/前端"）

    Args:
        category: 分类路径
        limit: 返回数量上限（1-200，默认 50）
    """
    return await _call_api("GET", f"/bookmarks/category/{category}", params={"limit": min(limit, 200)})


@mcp.tool()
async def add_bookmark(
    url: str,
    title: str,
    description: str = "",
    tags: Optional[List[str]] = None,
    category: str = "",
) -> Dict[str, Any]:
    """新增书签

    Args:
        url: 书签 URL（必填）
        title: 标题（必填）
        description: 描述（可选）
        tags: tag 列表（可选）
        category: 分类路径（可选）
    """
    if not url.strip() or not title.strip():
        return {"status": "error", "error": "url 和 title 必填"}
    return await _call_api("POST", "/bookmark", json_body={
        "url": url, "title": title, "description": description,
        "tags": tags or [], "category": category,
    })


@mcp.tool()
async def update_bookmark(
    bookmark_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    category: Optional[str] = None,
) -> Dict[str, Any]:
    """更新书签（只改传入字段）

    Args:
        bookmark_id: 书签 ID（必填）
        title: 新标题（可选）
        description: 新描述（可选）
        tags: 新 tag 列表（可选）
        category: 新分类（可选）
    """
    updates = {k: v for k, v in {"title": title, "description": description, "tags": tags, "category": category}.items() if v is not None}
    if not updates:
        return {"status": "error", "error": "至少要传一个字段"}
    updates["id"] = bookmark_id
    return await _call_api("POST", "/bookmark/update", json_body=updates)


@mcp.tool()
async def delete_bookmark(bookmark_id: str) -> Dict[str, Any]:
    """删除书签（**不可逆**）

    Args:
        bookmark_id: 书签 ID（必填）
    """
    return await _call_api("POST", "/bookmark/delete", json_body={"id": bookmark_id})


@mcp.tool()
async def batch_organize(
    bookmarks: List[Dict[str, Any]],
    action: str = "update",
) -> Dict[str, Any]:
    """批量操作（复用 `/v1/bookmarks/batch`）

    Args:
        bookmarks: 要更新的书签列表，每项含 id + 要改的字段
        action: 操作类型（默认 update）
    """
    return await _call_api("POST", "/bookmarks/batch", json_body={"bookmarks": bookmarks, "action": action})


@mcp.tool()
async def import_from_file(file_path: str, format: str = "html") -> Dict[str, Any]:
    """从 HTML 文件导入（复用 /v1/scripts/parse）

    Args:
        file_path: HTML 文件绝对路径（必填）
        format: 文件格式（默认 html）
    """
    from pathlib import Path
    if not Path(file_path).exists():
        return {"status": "error", "error": f"文件不存在: {file_path}"}
    return await _call_api("POST", "/scripts/process", json_body={"file": file_path})


# ============================================================================
# v2 工具
# ============================================================================


@mcp.tool()
async def sync_status():
    """Chrome 扩展同步状态"""
    return await _call_api("GET", "/bookmark/sync-status")


# ============================================================================
# 本地浏览器书签读取（无需安装扩展，降级方案）
# ============================================================================

import json
import platform
import subprocess
from pathlib import Path
from urllib.parse import urlparse


@dataclass(frozen=True)
class BrowserProfile:
    """浏览器 profile 描述（不可变）"""
    name: str           # "Chrome"
    os_path: str        # 完整路径，如 ~/Library/Application Support/Google/Chrome
    profile: str        # "Default" / "Profile 1"
    bookmarks_file: str # "Bookmarks"（绝对路径）


# 各浏览器在三大 OS 下的 user data 根目录
_BROWSER_PATHS: Dict[str, Dict[str, str]] = {
    "chrome": {
        "Darwin":  "~/Library/Application Support/Google/Chrome",
        "Windows": "%LOCALAPPDATA%\\Google\\Chrome\\User Data",
        "Linux":   "~/.config/google-chrome",
    },
    "edge": {
        "Darwin":  "~/Library/Application Support/Microsoft Edge",
        "Windows": "%LOCALAPPDATA%\\Microsoft\\Edge\\User Data",
        "Linux":   "~/.config/microsoft-edge",
    },
    "brave": {
        "Darwin":  "~/Library/Application Support/BraveSoftware/Brave-Browser",
        "Windows": "%LOCALAPPDATA%\\BraveSoftware\\Brave-Browser\\User Data",
        "Linux":   "~/.config/BraveSoftware/Brave-Browser",
    },
    "arc": {
        "Darwin":  "~/Library/Application Support/Arc/User Data",
        "Windows": "%LOCALAPPDATA%\\Arc\\User Data",
        "Linux":   "",  # Arc 不支持 Linux
    },
}


def _expand_path(p: str) -> str:
    """展开 ~ 和 Windows 环境变量"""
    if not p:
        return ""
    expanded = os.path.expanduser(os.path.expandvars(p))
    return os.path.normpath(expanded)


def _is_browser_running(browser: str) -> bool:
    """检测浏览器进程是否在跑

    macOS 注意：不能用 pgrep -f "chrome"，会误匹配 Electron 应用
    （百度网盘/Marvis/VSCode 都带 chrome_crashpad_handler）。改用精确路径匹配。
    """
    system = platform.system()

    # 每个浏览器在每个 OS 的可执行文件路径片段（精确匹配，避免误报）
    PROC_PATHS = {
        "Darwin": {
            "chrome": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "edge":   "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "brave":  "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
            "arc":    "/Applications/Arc.app/Contents/MacOS/Arc",
        },
        "Linux": {
            "chrome": "/opt/google/chrome/chrome",
            "edge":   "/opt/microsoft/msedge/msedge",
            "brave":  "/opt/brave.com/brave/brave",
            "arc":    "",  # Arc 不支持 Linux
        },
        "Windows": {
            "chrome": "chrome.exe",
            "edge":   "msedge.exe",
            "brave":  "brave.exe",
            "arc":    "Arc.exe",
        },
    }

    target = PROC_PATHS.get(system, {}).get(browser, "")
    if not target:
        return False

    try:
        if system in ("Darwin", "Linux"):
            # ps -ef 看 COMM（进程名）列；用 grep -F 精确匹配路径
            result = subprocess.run(
                ["pgrep", "-f", target],
                capture_output=True, text=True, timeout=3,
            )
            # 过滤掉 pgrep 自己
            pids = [p for p in result.stdout.strip().split("\n") if p and p != str(subprocess.os.getpid())]
            return len(pids) > 0
        elif system == "Windows":
            output = subprocess.check_output(
                ["tasklist"], text=True, timeout=3, errors="ignore",
            )
            return target.lower() in output.lower()
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        logger.warning(f"检测 {browser} 运行状态失败: {e}")

    return False


def _detect_profiles(browser: str) -> List[BrowserProfile]:
    """检测浏览器所有可用 profile"""
    system = platform.system()
    raw_path = _BROWSER_PATHS.get(browser, {}).get(system, "")
    user_data = _expand_path(raw_path)

    if not user_data or not os.path.isdir(user_data):
        return []

    # 找到所有 profile 目录（Default / Profile 1 / Profile 2 ...）
    profiles: List[BrowserProfile] = []
    candidates = ["Default"] + sorted(
        d for d in os.listdir(user_data)
        if d.startswith("Profile ") and os.path.isdir(os.path.join(user_data, d))
    )

    for profile in candidates:
        bm_file = os.path.join(user_data, profile, "Bookmarks")
        if os.path.isfile(bm_file):
            browser_name = {"chrome": "Chrome", "edge": "Edge",
                            "brave": "Brave", "arc": "Arc"}.get(browser, browser)
            profiles.append(BrowserProfile(
                name=f"{browser_name} ({profile})",
                os_path=user_data,
                profile=profile,
                bookmarks_file=bm_file,
            ))

    return profiles


def _flatten_chrome_tree(roots: Dict, folder_path: str = "") -> List[Dict[str, str]]:
    """把 Chrome 书签树递归展平为 [{url, title, folder_path}, ...]"""
    result: List[Dict[str, str]] = []

    def walk(node: Dict, current_path: str) -> None:
        node_type = node.get("type")
        if node_type == "url":
            url = node.get("url", "").strip()
            title = node.get("name", "").strip()
            if url and title and url.startswith(("http://", "https://")):
                result.append({
                    "url": url,
                    "title": title,
                    "folder_path": current_path,
                })
        elif node_type == "folder":
            folder_name = node.get("name", "").strip() or "未命名"
            new_path = f"{current_path}/{folder_name}" if current_path else folder_name
            for child in node.get("children", []):
                walk(child, new_path)

    for root in roots.values():
        if isinstance(root, dict):
            # 顶层 root 的 name 就是分类（书签栏 / 其他书签 / 移动书签）
            root_name = root.get("name", "").strip() or "未分类"
            for child in root.get("children", []):
                walk(child, root_name)

    return result


@mcp.tool()
async def sync_from_chrome(
    browser: str = "chrome",
    profile: str = "Default",
    exclude_patterns: Optional[List[str]] = None,
    dry_run: bool = False,
    batch_size: int = 50,
) -> Dict[str, Any]:
    """从本地浏览器读取书签并推送到 admin（无需 Chrome 扩展）。

    适用场景：不想/不便安装 Chrome 扩展时，用作降级方案。

    ⚠️ 重要：请先完全关闭浏览器（⌘Q / Alt+F4），否则可能读到损坏数据。

    Args:
        browser: 浏览器类型，支持 chrome / edge / brave / arc
        profile: profile 名称，Default 或 Profile 1/2/...
        exclude_patterns: 排除规则（正则表达式，匹配 url 或 title 跳过）
                          例：["*bank*", "*internal*", "github.com/private"]
                          防止误同步私密书签
        dry_run: 仅读取和解析，不实际推送到 admin
        batch_size: 每批推送到 admin 的书签数量（默认 50）

    Returns:
        {
            "status": "success" | "error",
            "browser": "...",
            "profile": "...",
            "browser_running": bool,
            "total_read": int,
            "total_excluded": int,  # 被 exclude_patterns 过滤掉的数量
            "sample": [{url, title, folder_path}, ...] (前 5 条),
            "stats": {added, skipped, errors} (仅在非 dry_run 时),
            "message": "...",
        }
    """
    import re
    browser = browser.lower()
    if browser not in _BROWSER_PATHS:
        return {"status": "error", "error": f"不支持的浏览器: {browser}（支持: {list(_BROWSER_PATHS)}）"}

    # 1. 检测 profile 是否存在
    profiles = _detect_profiles(browser)
    if not profiles:
        return {
            "status": "error",
            "error": f"未检测到 {browser} 浏览器（可能未安装或路径异常）",
            "checked_path": _expand_path(_BROWSER_PATHS[browser].get(platform.system(), "")),
        }

    target = next((p for p in profiles if p.profile == profile), None)
    if not target:
        available = [p.profile for p in profiles]
        return {
            "status": "error",
            "error": f"profile '{profile}' 不存在",
            "available_profiles": available,
        }

    # 2. 检测浏览器是否在跑
    is_running = _is_browser_running(browser)
    if is_running:
        return {
            "status": "error",
            "error": f"{target.name} 正在运行！请先完全关闭浏览器（⌘Q / Alt+F4），再重试。",
            "browser_running": True,
            "tip": "为避免 SQLite 锁冲突，必须完全关闭浏览器后才能读取 Bookmarks JSON。",
        }

    # 3. 读取 Bookmarks JSON
    try:
        with open(target.bookmarks_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        return {
            "status": "error",
            "error": f"读取 Bookmarks 文件失败: {e}",
            "tip": "可能是浏览器未完全关闭导致文件损坏。",
        }

    # 4. 解析嵌套结构
    bookmarks = _flatten_chrome_tree(data.get("roots", {}))

    if not bookmarks:
        return {
            "status": "success",
            "browser_running": False,
            "total_read": 0,
            "message": "浏览器中没有可同步的书签",
        }

    # 4.5 应用 exclude_patterns 过滤（隐私保护）
    total_excluded = 0
    if exclude_patterns:
        # 编译成正则
        compiled_patterns = []
        for p in exclude_patterns:
            try:
                compiled_patterns.append(re.compile(p, re.IGNORECASE))
            except re.error as e:
                return {
                    "status": "error",
                    "error": f"exclude_patterns 格式错误: {p!r} - {e}",
                }

        filtered = []
        for bm in bookmarks:
            url = bm.get("url", "")
            title = bm.get("title", "")
            if any(p.search(url) or p.search(title) for p in compiled_patterns):
                total_excluded += 1
            else:
                filtered.append(bm)
        bookmarks = filtered

    # 5. dry_run 直接返回
    if dry_run:
        return {
            "status": "success",
            "browser": target.name,
            "profile": target.profile,
            "browser_running": False,
            "dry_run": True,
            "total_read": len(bookmarks),
            "total_excluded": total_excluded,
            "sample": bookmarks[:5],
            "message": f"dry_run 模式：读取了 {len(bookmarks)} 条（过滤 {total_excluded}），未推送到 admin",
        }

    # 5. dry_run 直接返回
    if dry_run:
        return {
            "status": "success",
            "browser": target.name,
            "profile": target.profile,
            "browser_running": False,
            "dry_run": True,
            "total_read": len(bookmarks),
            "sample": bookmarks[:5],
            "message": f"dry_run 模式：读取了 {len(bookmarks)} 条，未推送到 admin",
        }

    # 6. 批量推送到 admin
    total_added = 0
    total_skipped = 0
    total_errors = 0
    all_errors: List[Dict] = []

    for i in range(0, len(bookmarks), batch_size):
        batch = bookmarks[i:i + batch_size]
        result = await _call_api("POST", "/bookmarks/sync-batch",
                                 json_body={"bookmarks": batch})
        if result.get("status") == "success":
            data_payload = result.get("data", {})
            stats = data_payload.get("stats", {})
            total_added += stats.get("added", 0)
            total_skipped += stats.get("skipped", 0)
            total_errors += stats.get("errors", 0)
            all_errors.extend(data_payload.get("errors", []))
        else:
            total_errors += len(batch)
            all_errors.append({"batch_start": i, "error": result.get("error")})

    return {
        "status": "success",
        "browser": target.name,
        "profile": target.profile,
        "browser_running": False,
        "total_read": len(bookmarks),
        "total_excluded": total_excluded,
        "pushed_to_admin": True,
        "stats": {
            "added": total_added,
            "skipped": total_skipped,
            "errors": total_errors,
        },
        "errors_sample": all_errors[:5],
        "message": (
            f"从 {target.name} 读取 {len(bookmarks)} 条"
            + (f"（过滤 {total_excluded} 条）" if total_excluded else "")
            + f"，新增 {total_added}，跳过（重复） {total_skipped}，失败 {total_errors}"
        ),
    }


@mcp.tool()
async def list_chrome_profiles(browser: str = "chrome") -> Dict[str, Any]:
    """列出本机已安装浏览器及其 profile（辅助 sync_from_chrome 选择参数）。

    Args:
        browser: 浏览器类型，chrome / edge / brave / arc

    Returns:
        {
            "status": "success" | "error",
            "browser": "chrome",
            "running": bool,
            "profiles": [{name, profile, bookmarks_file}, ...],
            "message": "...",
        }
    """
    browser = browser.lower()
    if browser not in _BROWSER_PATHS:
        return {"status": "error", "error": f"不支持的浏览器: {browser}"}

    profiles = _detect_profiles(browser)
    running = _is_browser_running(browser)

    return {
        "status": "success",
        "browser": browser,
        "running": running,
        "profiles": [
            {
                "name": p.name,
                "profile": p.profile,
                "bookmarks_file": p.bookmarks_file,
            }
            for p in profiles
        ],
        "message": (
            f"{'⚠️ 浏览器在运行，请先关闭' if running else '✓ 浏览器未运行，可以同步'}"
            f"，检测到 {len(profiles)} 个 profile"
        ),
    }


# ============================================================================
# v3 工具 - 分类引擎
# ============================================================================


@mcp.tool()
async def categorize_bookmark(url: str, title: str, description: str = "", folder_path: str = "", max_depth: int = 2):
    """对单个书签分类（自定义嵌套层数）"""
    return await _call_api("POST", "/bookmark/categorize", json_body={
        "url": url, "title": title, "description": description,
        "folder_path": folder_path, "max_depth": max_depth,
    })


@mcp.tool()
async def batch_categorize(bookmark_ids: Optional[List[str]] = None, max_depth: int = 2, strategy_priority: Optional[List[str]] = None, dry_run: bool = True):
    """批量分类"""
    return await _call_api("POST", "/bookmarks/categorize-batch", json_body={
        "bookmark_ids": bookmark_ids, "max_depth": max_depth,
        "strategy_priority": strategy_priority, "dry_run": dry_run,
    })


@mcp.tool()
async def get_categorization_config():
    """查看分类配置"""
    return await _call_api("GET", "/categorization/config")


@mcp.tool()
async def update_categorization_config(max_depth: Optional[int] = None, strategy_enabled: Optional[Dict[str, bool]] = None, strategy_priority: Optional[Dict[str, int]] = None):
    """动态更新分类配置"""
    body = {}
    if max_depth is not None:
        body["max_depth"] = max_depth
    strategies_update = {}
    if strategy_enabled:
        for k, v in strategy_enabled.items():
            strategies_update.setdefault(k, {})["enabled"] = v
    if strategy_priority:
        for k, v in strategy_priority.items():
            strategies_update.setdefault(k, {})["priority"] = v
    if strategies_update:
        body["strategies"] = strategies_update
    return await _call_api("POST", "/categorization/config", json_body=body)


# ============================================================================
# v4 工具 - 复用 admin 现有清洗端点（不再自造）
# ============================================================================


@mcp.tool()
async def deduplicate_bookmarks() -> Dict[str, Any]:
    """去重书签（复用 admin `/v1/bookmarks/deduplicate`）

    按 URL 精确去重，保留第一个出现的。

    Returns:
        {original_count, duplicate_count, current_count, message}
    """
    return await _call_api("POST", "/bookmarks/deduplicate")


@mcp.tool()
async def analyze_bookmarks(
    scope: str = "all",
    bookmark_ids: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """AI 智能分析书签（复用 `/v1/scripts/analyze`）

    Args:
        scope: 分析范围
            - all: 全部
            - duplicates: 只分析重复
            - dead_links: 只分析死链
            - untagged: 只分析未打 tag 的
        bookmark_ids: 自定义范围（None = 全部）

    Returns:
        suggestions 列表
    """
    # 复用 AI suggest 端点
    if scope == "duplicates":
        return await _call_api("POST", "/ai/suggest", json_body={"scope": "duplicates"})
    elif scope == "dead_links":
        return await _call_api("POST", "/ai/suggest", json_body={"scope": "dead_links"})
    elif scope == "untagged":
        return await _call_api("POST", "/ai/suggest", json_body={"scope": "untagged"})
    else:
        return await _call_api("POST", "/scripts/analyze", json_body={"scope": "all"})


@mcp.tool()
async def parse_bookmark_html(file_path: str) -> Dict[str, Any]:
    """解析 HTML 书签文件（复用 `/v1/scripts/parse`）

    Args:
        file_path: Chrome/Firefox 导出的 HTML 文件路径
    """
    from pathlib import Path
    if not Path(file_path).exists():
        return {"status": "error", "error": f"文件不存在: {file_path}"}

    # 直接调用 scripts/parse（需要 multipart 上传）
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f, 'text/html')}
            resp = await client.post("/scripts/parse", files=files)
            resp.raise_for_status()
            return {"status": "success", "data": resp.json()}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
async def list_scripts() -> Dict[str, Any]:
    """列出 admin 已注册的分析脚本（复用 `/v1/scripts`）

    Returns:
        scripts: [{name, description, author, ...}]
    """
    return await _call_api("GET", "/scripts")


@mcp.tool()
async def list_tags(limit: int = 100, offset: int = 0) -> Dict[str, Any]:
    """列出所有 tag（复用 `/v1/tags`）"""
    return await _call_api("GET", "/tags", params={"limit": min(limit, 500), "offset": max(offset, 0)})


@mcp.tool()
async def ai_suggest_one(
    url: str,
    title: str,
    suggest_type: str = "title",  # title/alias/tags/category/summary
) -> Dict[str, Any]:
    """AI 优化单个书签（复用 `/v1/ai/suggest`）

    Args:
        url: 书签 URL
        title: 当前标题
        suggest_type: 建议类型
            - title: 优化标题
            - alias: 生成别名
            - tags: 推荐 tag
            - category: 推荐分类
            - summary: 生成摘要
    """
    return await _call_api("POST", "/ai/suggest", json_body={
        "type": suggest_type,
        "url": url,
        "title": title,
    })


@mcp.tool()
async def ai_suggest_batch(
    bookmark_ids: Optional[List[str]] = None,
    suggest_type: str = "tags",
) -> Dict[str, Any]:
    """批量 AI 建议（复用 `/v1/tags/batch-generate`）

    Args:
        bookmark_ids: 要生成 tag 的书签 ID 列表（None = 全部未打 tag）
        suggest_type: 建议类型
    """
    return await _call_api("POST", "/tags/batch-generate", json_body={
        "ids": bookmark_ids or [],
        "type": suggest_type,
    })


@mcp.tool()
async def merge_tags(source_tag_id: str, target_tag_id: str) -> Dict[str, Any]:
    """合并 tag（复用 `/v1/tags/<id>/merge`）"""
    return await _call_api("POST", f"/tags/{source_tag_id}/merge", json_body={"target_id": target_tag_id})


@mcp.tool()
async def batch_delete(bookmark_ids: List[str]) -> Dict[str, Any]:
    """批量删除书签（复用 `/v1/bookmarks/batch-delete`，**不可逆**）"""
    return await _call_api("POST", "/bookmarks/batch-delete", json_body={"ids": bookmark_ids})


@mcp.tool()
async def batch_update_bookmarks(
    bookmark_ids: List[str],
    updates: Dict[str, Any],
) -> Dict[str, Any]:
    """批量更新书签字段（复用 `/v1/bookmarks/batch-update`）"""
    return await _call_api("POST", "/bookmarks/batch-update", json_body={
        "ids": bookmark_ids,
        "updates": updates,
    })


@mcp.tool()
async def export_bookmarks(
    format: str = "html",
    bookmark_ids: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """导出书签（复用 `/v1/bookmarks/export`）

    Args:
        format: 导出格式（html / json / csv）
        bookmark_ids: 自定义范围（None = 全部）
    """
    return await _call_api("POST", "/bookmarks/export", json_body={
        "format": format,
        "ids": bookmark_ids,
    })


@mcp.tool()
async def get_stats() -> Dict[str, Any]:
    """书签统计（复用 `/v1/bookmarks/stats`）"""
    return await _call_api("GET", "/bookmarks/stats")


@mcp.tool()
async def get_folder_tree() -> Dict[str, Any]:
    """文件夹树（复用 `/v1/folders`）"""
    return await _call_api("GET", "/folders")


@mcp.tool()
async def fetch_metadata(url: str) -> Dict[str, Any]:
    """抓取 URL 元数据（复用 `/v1/bookmark/<url>/metadata` GET）

    实际抓取网页 og:title / description / image。
    """
    return await _call_api("GET", f"/bookmark/{url}/metadata")


@mcp.tool()
async def record_visit(url: str) -> Dict[str, Any]:
    """记录书签访问（复用 `/v1/bookmark/<url>/visit`）"""
    return await _call_api("POST", f"/bookmark/{url}/visit")


if __name__ == "__main__":
    logger.info(f"Starting Bookmark MCP v4, API: {BOOKMARK_API_BASE}")
    mcp.run()
